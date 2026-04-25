"""
Voice Chat Userbot - Main Entry Point
"""

import asyncio
import importlib

from pyrogram import Client
from pytgcalls import GroupCallFactory

from config import Config
from state import state
from database import init_db, get_all_groups

# ── Init DB ──────────────────────────────────────────────────────────────────
init_db()

# ── Pyrogram client ──────────────────────────────────────────────────────────
app = Client(
    "vcbot_session",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.SESSION_STRING if Config.SESSION_STRING else None,
)

# ── GroupCallFactory (pytgcalls 3.x) ─────────────────────────────────────────
factory = GroupCallFactory(app)
vc = factory.get_file_group_call()  # audio file play karne ke liye
state.vc = vc
state.factory = factory

# ── Load default active group from DB ────────────────────────────────────────
saved = get_all_groups()
if saved:
    first = saved[0]
    state.group_id = first["group_id"]
    state.volume   = first["volume"]
    state.pitch    = first["pitch"]
    state.echo_enabled = bool(first["echo"])
    state.join_as  = first["join_as"]
elif Config.GROUP_ID:
    state.group_id = Config.GROUP_ID
    state.volume   = Config.DEFAULT_VOLUME
    state.join_as  = Config.JOIN_AS

# ── Load plugins ─────────────────────────────────────────────────────────────
PLUGINS = [
    "plugins.play",
    "plugins.live",
    "plugins.download",
    "plugins.kernel",
    "plugins.audio_controls",
    "plugins.record",
    "plugins.utils",
    "plugins.groups",
    "plugins.help",
]

for plugin in PLUGINS:
    try:
        importlib.import_module(plugin)
        print(f"✅ Loaded: {plugin}")
    except Exception as e:
        print(f"❌ Failed: {plugin} — {e}")


# ── Start ────────────────────────────────────────────────────────────────────
async def main():
    print("\n🎙️ Voice Chat Userbot Starting...")
    groups = get_all_groups()
    print(f"   Saved Groups : {len(groups)}")
    print(f"   Active Group : {state.group_id or 'Not set'}")
    print(f"   Volume       : {state.volume}")

    await app.start()

    me = await app.get_me()
    print(f"✅ Logged in as: {me.first_name} (@{me.username})")
    print("📋 /vchelp — all commands\n")

    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped.")
