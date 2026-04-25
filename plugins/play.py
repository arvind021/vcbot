"""
Play Commands Plugin
/setgroup, /setjoinas, /volume, /pitch, /echo
/skip, /stop, /pause, /resume, /leavegroup
Auto-play when voice/audio message received
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import AudioQuality
from state import state


def vc():
    return state.vc


@Client.on_message(filters.command("setgroup") & filters.me)
async def setgroup(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit("❌ Usage: `/setgroup -1001234567890`")
    try:
        state.group_id = int(args[1])
        await message.edit(f"✅ Group ID set: `{state.group_id}`")
    except ValueError:
        await message.edit("❌ Invalid Group ID.")


@Client.on_message(filters.command("setjoinas") & filters.me)
async def setjoinas(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit("❌ Usage: `/setjoinas -100xxxxxxxxx`")
    try:
        state.join_as = int(args[1])
        await message.edit(f"✅ Join-as set: `{state.join_as}`")
    except ValueError:
        await message.edit("❌ Invalid Channel ID.")


@Client.on_message(filters.command("volume") & filters.me)
async def set_volume(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(f"🔊 Current Volume: `{state.volume}`\nUsage: `/volume 100`")
    try:
        vol = int(args[1])
        if not 1 <= vol <= 200:
            return await message.edit("❌ Volume must be 1–200.")
        state.volume = vol
        if state.is_playing and state.group_id:
            await vc().change_volume_call(state.group_id, vol)
        await message.edit(f"🔊 Volume: `{vol}`")
    except ValueError:
        await message.edit("❌ Invalid value.")


@Client.on_message(filters.command("pitch") & filters.me)
async def set_pitch(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(f"🎼 Current Pitch: `{state.pitch}`\nUsage: `/pitch 1.5`")
    try:
        state.pitch = float(args[1])
        await message.edit(f"🎼 Pitch: `{state.pitch}` _(applies to next stream)_")
    except ValueError:
        await message.edit("❌ Invalid value.")


@Client.on_message(filters.command("echo") & filters.me)
async def set_echo(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        st = "ON ✅" if state.echo_enabled else "OFF ❌"
        return await message.edit(f"🎚 Echo: `{st}`\nUsage: `/echo on` or `/echo off`")
    p = args[1].lower()
    if p == "on":
        state.echo_enabled = True
        await message.edit("🎚 Echo **ON** ✅")
    elif p == "off":
        state.echo_enabled = False
        await message.edit("🎚 Echo **OFF** ❌")
    else:
        await message.edit("❌ Usage: `/echo on|off`")


@Client.on_message(filters.command("skip") & filters.me)
async def skip_audio(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ Set group first: `/setgroup [id]`")
    try:
        if state.queue:
            nxt = state.queue.pop(0)
            state.current_audio = nxt
            await vc().change_stream(state.group_id, MediaStream(nxt))
            await message.edit(f"⏭ Skipped! Now playing: `{nxt}`")
        else:
            await vc().leave_call(state.group_id)
            state.is_playing = False
            state.current_audio = None
            await message.edit("⏭ Skipped! Queue empty, left VC.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("stop") & filters.me)
async def stop_audio(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ Set group first.")
    try:
        await vc().leave_call(state.group_id)
        state.queue.clear()
        state.current_audio = None
        state.is_playing = False
        state.is_paused = False
        await message.edit("⏹ Stopped & queue cleared.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("pause") & filters.me)
async def pause_audio(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ Set group first.")
    try:
        await vc().pause_stream(state.group_id)
        state.is_paused = True
        await message.edit("⏸ Paused.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("resume") & filters.me)
async def resume_audio(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ Set group first.")
    try:
        await vc().resume_stream(state.group_id)
        state.is_paused = False
        await message.edit("▶️ Resumed.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("leavegroup") & filters.me)
async def leave_group(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ No group set.")
    try:
        await vc().leave_call(state.group_id)
        state.is_playing = False
        state.is_paused = False
        state.current_audio = None
        await message.edit(f"🍄 Left VC in `{state.group_id}`.")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.me & (filters.voice | filters.audio))
async def auto_play(client: Client, message: Message):
    if not state.group_id:
        return
    msg = await message.reply("⬇️ Downloading...")
    try:
        file_path = await message.download()
        if state.is_playing:
            state.queue.append(file_path)
            return await msg.edit(f"📋 Added to queue. Position: `{len(state.queue)}`")
        state.current_audio = file_path
        state.is_playing = True
        join_as = state.join_as if state.join_as else None
        await vc().join_call(
            state.group_id,
            MediaStream(file_path, audio_parameters=AudioQuality.HIGH),
            join_as=join_as,
        )
        await msg.edit(
            f"🎙️ **Playing in VC!**\n"
            f"🔊 Volume: `{state.volume}`  🎼 Pitch: `{state.pitch}`  "
            f"🎚 Echo: `{'ON' if state.echo_enabled else 'OFF'}`"
        )
    except Exception as e:
        await msg.edit(f"❌ Play error: `{e}`")
