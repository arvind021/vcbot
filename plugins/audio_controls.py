"""
Audio Controls Plugin
/level [1-25], /bass [0-15], /mute, /unmute
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from state import state
from plugins.play import get_pytgcalls


@Client.on_message(filters.command("level") & filters.me)
async def set_level(client: Client, message: Message):
    """
    /level [1-25] - Set volume level (maps to 0-200 internally)
    """
    args = message.command
    if len(args) < 2:
        current = round(state.volume / 8)  # map back to 1-25
        return await message.edit(f"🔊 Current Level: `{current}/25`\nUsage: `/level 15`")
    try:
        lvl = int(args[1])
        if not 1 <= lvl <= 25:
            return await message.edit("❌ Level must be between 1 and 25.")
        vol = lvl * 8  # map 1-25 → 8-200
        state.volume = vol
        vc = get_pytgcalls(client)
        if state.is_playing and state.group_id:
            await vc.change_volume_call(state.group_id, vol)
        await message.edit(f"🔊 Volume Level: `{lvl}/25` (internal: `{vol}`)")
    except ValueError:
        await message.edit("❌ Invalid level.")


@Client.on_message(filters.command("bass") & filters.me)
async def set_bass(client: Client, message: Message):
    """
    /bass [0-15] - Set bass reduction level
    Note: Actual bass EQ requires ffmpeg audio filter pipeline
    """
    args = message.command
    if len(args) < 2:
        return await message.edit(
            f"🎚 Bass Level: `{state.echo_params.get('bass', 0)}/15`\n"
            "Usage: `/bass 8`"
        )
    try:
        b = int(args[1])
        if not 0 <= b <= 15:
            return await message.edit("❌ Bass must be between 0 and 15.")
        state.echo_params["bass"] = b
        await message.edit(
            f"🎚 Bass set to `{b}/15`\n"
            f"_Will apply with next audio stream via ffmpeg filter._"
        )
    except ValueError:
        await message.edit("❌ Invalid bass value.")


@Client.on_message(filters.command("mute") & filters.me)
async def mute_assistant(client: Client, message: Message):
    """Mute the assistant in VC"""
    if not state.group_id:
        return await message.edit("❌ Not in any group.")
    vc = get_pytgcalls(client)
    try:
        await vc.mute_stream(state.group_id)
        await message.edit("🔇 **Muted.**")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("unmute") & filters.me)
async def unmute_assistant(client: Client, message: Message):
    """Unmute the assistant in VC"""
    if not state.group_id:
        return await message.edit("❌ Not in any group.")
    vc = get_pytgcalls(client)
    try:
        await vc.unmute_stream(state.group_id)
        await message.edit("🔊 **Unmuted.**")
    except Exception as e:
        await message.edit(f"❌ Error: `{e}`")
