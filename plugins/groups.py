"""
Multi-Group Management Plugin
/setgroup, /removegroup, /listgroups, /groupsettings
/groupvolume, /grouppitch, /groupecho, /groupjoinas
"""

from pyrogram import Client, filters
from pyrogram.types import Message
from database import (
    add_group, remove_group, get_all_groups,
    get_group, update_group
)
from state import state


# ─── /setgroup [group_id] [optional_name] ────────────────────────────────────
@Client.on_message(filters.command("setgroup") & filters.me)
async def setgroup(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit(
            "❌ Usage: `/setgroup -1001234567890 GroupName`\n"
            "Name optional hai."
        )
    try:
        gid = int(args[1])
        name = " ".join(args[2:]) if len(args) > 2 else ""

        # Telegram se group name fetch karne ki koshish
        if not name:
            try:
                chat = await client.get_chat(gid)
                name = chat.title or ""
            except Exception:
                name = ""

        add_group(gid, name)
        await message.edit(
            f"✅ **Group Added!**\n"
            f"🆔 ID: `{gid}`\n"
            f"📛 Name: `{name or 'Unknown'}`\n\n"
            f"Settings ke liye: `/groupsettings {gid}`"
        )
    except ValueError:
        await message.edit("❌ Invalid Group ID. Example: `-1001234567890`")


# ─── /removegroup [group_id] ──────────────────────────────────────────────────
@Client.on_message(filters.command("removegroup") & filters.me)
async def removegroup(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit("❌ Usage: `/removegroup -1001234567890`")
    try:
        gid = int(args[1])
        grp = get_group(gid)
        if not grp:
            return await message.edit(f"❌ Group `{gid}` database mein nahi hai.")
        remove_group(gid)
        await message.edit(f"🗑 **Removed:** `{grp['name'] or gid}`")
    except ValueError:
        await message.edit("❌ Invalid Group ID.")


# ─── /listgroups ──────────────────────────────────────────────────────────────
@Client.on_message(filters.command("listgroups") & filters.me)
async def listgroups(client: Client, message: Message):
    groups = get_all_groups()
    if not groups:
        return await message.edit(
            "📋 Koi group nahi hai.\n"
            "Add karo: `/setgroup -1001234567890`"
        )

    text = f"📋 **Saved Groups ({len(groups)}):**\n\n"
    for i, g in enumerate(groups, 1):
        name = g['name'] or "Unknown"
        gid = g['group_id']
        vol = g['volume']
        pitch = g['pitch']
        echo = "ON" if g['echo'] else "OFF"
        text += (
            f"**{i}.** {name}\n"
            f"   🆔 `{gid}`\n"
            f"   🔊 Vol: `{vol}` | 🎼 Pitch: `{pitch}` | 🎚 Echo: `{echo}`\n\n"
        )

    text += "▶️ Play karne ke liye: `/playgroup [group_id]`"
    await message.edit(text)


# ─── /groupsettings [group_id] ────────────────────────────────────────────────
@Client.on_message(filters.command("groupsettings") & filters.me)
async def groupsettings(client: Client, message: Message):
    args = message.command
    if len(args) < 2:
        return await message.edit("❌ Usage: `/groupsettings -1001234567890`")
    try:
        gid = int(args[1])
        g = get_group(gid)
        if not g:
            return await message.edit(f"❌ Group `{gid}` nahi mila. Pehle `/setgroup` karo.")
        await message.edit(
            f"⚙️ **Group Settings:**\n\n"
            f"📛 Name: `{g['name'] or 'Unknown'}`\n"
            f"🆔 ID: `{g['group_id']}`\n"
            f"🔊 Volume: `{g['volume']}`\n"
            f"🎼 Pitch: `{g['pitch']}`\n"
            f"🎚 Echo: `{'ON' if g['echo'] else 'OFF'}`\n"
            f"🙊 Join As: `{g['join_as'] or 'Self'}`\n"
            f"📅 Added: `{g['added_at']}`\n\n"
            f"Change karo:\n"
            f"`/groupvolume {gid} 100`\n"
            f"`/grouppitch {gid} 1.0`\n"
            f"`/groupecho {gid} on`\n"
            f"`/groupjoinas {gid} -100xxxxxxx`"
        )
    except ValueError:
        await message.edit("❌ Invalid Group ID.")


# ─── /groupvolume [group_id] [level] ─────────────────────────────────────────
@Client.on_message(filters.command("groupvolume") & filters.me)
async def groupvolume(client: Client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.edit("❌ Usage: `/groupvolume -1001234567890 100`")
    try:
        gid = int(args[1])
        vol = int(args[2])
        if not 1 <= vol <= 200:
            return await message.edit("❌ Volume 1–200 ke beech hona chahiye.")
        update_group(gid, volume=vol)
        # Live update if this group is currently active
        if state.group_id == gid and state.is_playing:
            await state.vc.change_volume_call(gid, vol)
        await message.edit(f"🔊 Group `{gid}` volume: `{vol}`")
    except ValueError:
        await message.edit("❌ Invalid values.")


# ─── /grouppitch [group_id] [pitch] ──────────────────────────────────────────
@Client.on_message(filters.command("grouppitch") & filters.me)
async def grouppitch(client: Client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.edit("❌ Usage: `/grouppitch -1001234567890 1.5`")
    try:
        gid = int(args[1])
        pitch = float(args[2])
        update_group(gid, pitch=pitch)
        await message.edit(f"🎼 Group `{gid}` pitch: `{pitch}`")
    except ValueError:
        await message.edit("❌ Invalid values.")


# ─── /groupecho [group_id] [on|off] ──────────────────────────────────────────
@Client.on_message(filters.command("groupecho") & filters.me)
async def groupecho(client: Client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.edit("❌ Usage: `/groupecho -1001234567890 on`")
    try:
        gid = int(args[1])
        val = 1 if args[2].lower() == "on" else 0
        update_group(gid, echo=val)
        status = "ON ✅" if val else "OFF ❌"
        await message.edit(f"🎚 Group `{gid}` echo: `{status}`")
    except ValueError:
        await message.edit("❌ Invalid Group ID.")


# ─── /groupjoinas [group_id] [channel_id] ────────────────────────────────────
@Client.on_message(filters.command("groupjoinas") & filters.me)
async def groupjoinas(client: Client, message: Message):
    args = message.command
    if len(args) < 3:
        return await message.edit("❌ Usage: `/groupjoinas -1001234567890 -100xxxxxxxxx`")
    try:
        gid = int(args[1])
        cid = int(args[2])
        update_group(gid, join_as=cid)
        await message.edit(f"🙊 Group `{gid}` join-as: `{cid}`")
    except ValueError:
        await message.edit("❌ Invalid values.")


# ─── /playgroup [group_id] ────────────────────────────────────────────────────
@Client.on_message(filters.command("playgroup") & filters.me)
async def playgroup(client: Client, message: Message):
    """Switch active group for playback"""
    args = message.command
    if len(args) < 2:
        return await message.edit("❌ Usage: `/playgroup -1001234567890`")
    try:
        gid = int(args[1])
        g = get_group(gid)
        if not g:
            return await message.edit(
                f"❌ Group `{gid}` saved nahi hai.\n"
                f"Pehle `/setgroup {gid}` karo."
            )
        # Load this group's settings into active state
        state.group_id = gid
        state.volume = g['volume']
        state.pitch = g['pitch']
        state.echo_enabled = bool(g['echo'])
        state.join_as = g['join_as']

        await message.edit(
            f"✅ **Active Group Changed!**\n"
            f"📛 `{g['name'] or gid}`\n"
            f"🔊 Vol: `{state.volume}` | 🎼 Pitch: `{state.pitch}` | 🎚 Echo: `{'ON' if state.echo_enabled else 'OFF'}`\n\n"
            f"Ab voice/audio bhejo ya `/audio [name]` karo."
        )
    except ValueError:
        await message.edit("❌ Invalid Group ID.")
