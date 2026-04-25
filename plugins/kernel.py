"""
Remote Kernel Plugin
/join, /leave, /leaveall, /leaverecord, /leaveplay
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import MediaStream
from pytgcalls.types.stream import AudioQuality
from state import state
from plugins.play import get_pytgcalls


@Client.on_message(filters.command("join") & filters.me)
async def kernel_join(client: Client, message: Message):
    """Join both Record VC and Play VC"""
    if not state.group_id:
        return await message.edit("❌ Set group first: `/setgroup [id]`")
    vc = get_pytgcalls(client)
    errors = []
    try:
        # Join play VC
        join_as = state.join_as if state.join_as else None
        await vc.join_call(
            state.group_id,
            MediaStream("silence.ogg"),  # silent stream as placeholder
            join_as=join_as,
        )
        state.play_vc_joined = True
    except Exception as e:
        errors.append(f"Play VC: `{e}`")

    state.record_vc_joined = True  # Mark record as joined (handled separately)

    if errors:
        await message.edit(f"⚠️ Joined with errors:\n" + "\n".join(errors))
    else:
        await message.edit(
            f"✅ **Joined Both VCs!**\n"
            f"🎤 Record VC: `{'Joined' if state.record_vc_joined else 'Failed'}`\n"
            f"▶️ Play VC: `{'Joined' if state.play_vc_joined else 'Failed'}`"
        )


@Client.on_message(filters.command("leave") & filters.me)
async def kernel_leave(client: Client, message: Message):
    """Leave both Record VC and Play VC"""
    if not state.group_id:
        return await message.edit("❌ No active group.")
    vc = get_pytgcalls(client)
    try:
        await vc.leave_call(state.group_id)
        state.play_vc_joined = False
        state.record_vc_joined = False
        state.is_playing = False
        await message.edit("🚪 **Left both VCs.**")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("leaveall") & filters.me)
async def kernel_leaveall(client: Client, message: Message):
    """Leave all active VCs"""
    vc = get_pytgcalls(client)
    try:
        calls = await vc.calls
        count = len(calls)
        for call in calls:
            try:
                await vc.leave_call(call.chat_id)
            except Exception:
                pass
        state.play_vc_joined = False
        state.record_vc_joined = False
        state.is_playing = False
        state.live_active = False
        await message.edit(f"🚪 **Left all VCs!** (Total: `{count}`)")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("leaverecord") & filters.me)
async def kernel_leaverecord(client: Client, message: Message):
    """Leave only Record VC"""
    state.record_vc_joined = False
    state.is_recording = False
    await message.edit("🎤 **Left Record VC.**")


@Client.on_message(filters.command("leaveplay") & filters.me)
async def kernel_leaveplay(client: Client, message: Message):
    """Leave only Play VC"""
    if not state.group_id:
        return await message.edit("❌ No active group.")
    vc = get_pytgcalls(client)
    try:
        await vc.leave_call(state.group_id)
        state.play_vc_joined = False
        state.is_playing = False
        await message.edit("▶️ **Left Play VC.**")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
