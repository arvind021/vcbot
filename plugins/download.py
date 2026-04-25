"""
Downloaded Audios Plugin
/download - Download replied audio with a name
/audio - Play a downloaded audio by name
"""

import os
from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import AudioQuality
from state import state
from plugins.play import get_pytgcalls

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


@Client.on_message(filters.command("download") & filters.me)
async def download_audio(client: Client, message: Message):
    """
    Usage: /download [name]  (reply to an audio/voice message)
    Example: /download mysong
    """
    args = message.command
    reply = message.reply_to_message

    if not reply or not (reply.audio or reply.voice or reply.document):
        return await message.edit(
            "❌ Reply to an audio/voice message.\n"
            "Usage: `/download mysong` (reply to audio)"
        )

    name = args[1] if len(args) > 1 else f"audio_{len(state.downloaded_audios) + 1}"
    # Ensure .ogg extension for voice compatibility
    if not name.endswith((".ogg", ".mp3", ".m4a", ".flac", ".wav")):
        name += ".ogg"

    msg = await message.edit(f"⬇️ Downloading `{name}`...")
    try:
        file_path = await reply.download(file_name=os.path.join(DOWNLOAD_DIR, name))
        state.downloaded_audios[name] = file_path
        await msg.edit(
            f"✅ Downloaded as `{name}`\n"
            f"Play with: `/audio {name}`\n"
            f"Total saved: `{len(state.downloaded_audios)}`"
        )
    except Exception as e:
        await msg.edit(f"❌ Download failed: `{e}`")


@Client.on_message(filters.command("audio") & filters.me)
async def play_downloaded(client: Client, message: Message):
    """
    Usage: /audio mysong.ogg
    """
    args = message.command
    if len(args) < 2:
        if not state.downloaded_audios:
            return await message.edit("📂 No downloaded audios yet.\nUse `/download [name]` first.")
        files_list = "\n".join([f"• `{k}`" for k in state.downloaded_audios.keys()])
        return await message.edit(f"📂 **Downloaded Audios:**\n{files_list}\n\nUsage: `/audio [name.ogg]`")

    name = args[1]
    if name not in state.downloaded_audios:
        # Try to find in downloads dir directly
        path = os.path.join(DOWNLOAD_DIR, name)
        if os.path.exists(path):
            state.downloaded_audios[name] = path
        else:
            return await message.edit(
                f"❌ `{name}` not found.\n"
                f"Available: {', '.join(state.downloaded_audios.keys()) or 'None'}"
            )

    if not state.group_id:
        return await message.edit("❌ Set group first: `/setgroup [id]`")

    file_path = state.downloaded_audios[name]
    msg = await message.edit(f"🎵 Playing `{name}`...")
    try:
        vc = get_pytgcalls(client)
        join_as = state.join_as if state.join_as else None

        if state.is_playing:
            state.queue.append(file_path)
            await msg.edit(f"📋 `{name}` added to queue. Position: `{len(state.queue)}`")
        else:
            state.current_audio = file_path
            state.is_playing = True
            await vc.join_call(
                state.group_id,
                MediaStream(file_path, audio_parameters=AudioQuality.HIGH),
                join_as=join_as,
            )
            await msg.edit(f"🎵 **Playing:** `{name}`\n🔊 Volume: `{state.volume}`")
    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")
