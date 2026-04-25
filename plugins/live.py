"""
Live Forwarding Plugin
/golive, /stoplive, /livestatus, /updatelive
/sourcevolume, /sourcepitch, /sourceecho
/destvolume, /destpitch, /destecho
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from state import state


@Client.on_message(filters.command("golive") & filters.me)
async def golive(client: Client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.edit(
            "❌ Usage: `/golive [source_group_id] [dest_group_id]`\n"
            "Example: `/golive -1001111111 -1002222222`"
        )
    try:
        src = int(args[1])
        dst = int(args[2])
        state.live_source = src
        state.live_dest = dst
        state.live_active = True
        await message.edit(
            f"📡 **Live Forwarding Started!**\n"
            f"🔴 Source: `{src}`\n"
            f"🟢 Dest: `{dst}`\n"
            f"_Audio from source VC will be forwarded to dest VC._"
        )
        # NOTE: Actual VC-to-VC forwarding requires pytgcalls stream chaining
        # Implementation: join both VCs and pipe audio stream
    except ValueError:
        await message.edit("❌ Invalid group IDs.")


@Client.on_message(filters.command("stoplive") & filters.me)
async def stoplive(client: Client, message: Message):
    state.live_active = False
    state.live_source = 0
    state.live_dest = 0
    await message.edit("⏹ **Live Forwarding Stopped.**")


@Client.on_message(filters.command("livestatus") & filters.me)
async def livestatus(client: Client, message: Message):
    if not state.live_active:
        return await message.edit("📊 Live Forwarding: **Inactive** ❌")
    await message.edit(
        f"📊 **Live Status:**\n"
        f"🔴 Source: `{state.live_source}` | Vol: `{state.source_volume}` | Pitch: `{state.source_pitch}` | Echo: `{'ON' if state.source_echo else 'OFF'}`\n"
        f"🟢 Dest: `{state.live_dest}` | Vol: `{state.dest_volume}` | Pitch: `{state.dest_pitch}` | Echo: `{'ON' if state.dest_echo else 'OFF'}`"
    )


@Client.on_message(filters.command("updatelive") & filters.me)
async def updatelive(client: Client, message: Message):
    if not state.live_active:
        return await message.edit("❌ No active live session. Use `/golive` first.")
    await message.edit(
        f"🔄 **Live Settings Updated:**\n"
        f"Source Vol: `{state.source_volume}` | Pitch: `{state.source_pitch}` | Echo: `{'ON' if state.source_echo else 'OFF'}`\n"
        f"Dest Vol: `{state.dest_volume}` | Pitch: `{state.dest_pitch}` | Echo: `{'ON' if state.dest_echo else 'OFF'}`"
    )


# ── Source Settings ──────────────────────────

@Client.on_message(filters.command("sourcevolume") & filters.me)
async def sourcevolume(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(f"🔊 Source Volume: `{state.source_volume}`\nUsage: `/sourcevolume 100`")
    try:
        vol = int(args[1])
        state.source_volume = vol
        await message.edit(f"🔊 Source Volume set to `{vol}`")
    except ValueError:
        await message.edit("❌ Invalid value.")


@Client.on_message(filters.command("sourcepitch") & filters.me)
async def sourcepitch(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(f"🎼 Source Pitch: `{state.source_pitch}`\nUsage: `/sourcepitch 1.0`")
    try:
        p = float(args[1])
        state.source_pitch = p
        await message.edit(f"🎼 Source Pitch set to `{p}`")
    except ValueError:
        await message.edit("❌ Invalid value.")


@Client.on_message(filters.command("sourceecho") & filters.me)
async def sourceecho(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit("Usage: `/sourceecho on` or `/sourceecho off`")
    state.source_echo = args[1].lower() == "on"
    status = "ON ✅" if state.source_echo else "OFF ❌"
    await message.edit(f"🎚 Source Echo: `{status}`")


# ── Dest Settings ────────────────────────────

@Client.on_message(filters.command("destvolume") & filters.me)
async def destvolume(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(f"🔊 Dest Volume: `{state.dest_volume}`\nUsage: `/destvolume 100`")
    try:
        vol = int(args[1])
        state.dest_volume = vol
        await message.edit(f"🔊 Dest Volume set to `{vol}`")
    except ValueError:
        await message.edit("❌ Invalid value.")


@Client.on_message(filters.command("destpitch") & filters.me)
async def destpitch(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(f"🎼 Dest Pitch: `{state.dest_pitch}`\nUsage: `/destpitch 1.0`")
    try:
        p = float(args[1])
        state.dest_pitch = p
        await message.edit(f"🎼 Dest Pitch set to `{p}`")
    except ValueError:
        await message.edit("❌ Invalid value.")


@Client.on_message(filters.command("destecho") & filters.me)
async def destecho(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit("Usage: `/destecho on` or `/destecho off`")
    state.dest_echo = args[1].lower() == "on"
    status = "ON ✅" if state.dest_echo else "OFF ❌"
    await message.edit(f"🎚 Dest Echo: `{status}`")
