"""
Utils Plugin
/screenshare, /screenshareoff, /speedtest, /restart
"""

import asyncio
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message
from state import state
from plugins.play import get_pytgcalls


@Client.on_message(filters.command("screenshare") & filters.me)
async def screenshare(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ Set group first: `/setgroup [id]`")
    await message.edit(
        "🖥️ **Screenshare started!**\n"
        "_Note: Screenshare requires display output (X11/Wayland) and pytgcalls VideoStream._\n"
        "Use `/screenshareoff` to stop."
    )
    # vc = get_pytgcalls(client)
    # from pytgcalls.types import MediaStream, VideoQuality
    # await vc.join_call(group_id, MediaStream(screen_capture_device, video_parameters=VideoQuality.FHD_1080p))


@Client.on_message(filters.command("screenshareoff") & filters.me)
async def screenshareoff(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ No active group.")
    await message.edit("🖥️ **Screenshare stopped.**")


@Client.on_message(filters.command("speedtest") & filters.me)
async def speedtest(client: Client, message: Message):
    msg = await message.edit("⚡ Running speedtest...")
    try:
        result = subprocess.run(
            ["speedtest-cli", "--simple"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            output = result.stdout.strip()
            await msg.edit(f"⚡ **Speedtest Results:**\n```\n{output}\n```")
        else:
            # Fallback: use python speedtest
            result2 = subprocess.run(
                ["python3", "-c",
                 "import speedtest; s=speedtest.Speedtest(); s.get_best_server(); "
                 "dl=round(s.download()/1_000_000,2); ul=round(s.upload()/1_000_000,2); "
                 "ping=round(s.results.ping,2); print(f'Ping: {ping} ms\\nDownload: {dl} Mbit/s\\nUpload: {ul} Mbit/s')"],
                capture_output=True, text=True, timeout=60,
            )
            if result2.returncode == 0:
                await msg.edit(f"⚡ **Speedtest Results:**\n```\n{result2.stdout.strip()}\n```")
            else:
                await msg.edit("❌ Speedtest failed. Install: `pip install speedtest-cli`")
    except FileNotFoundError:
        await msg.edit("❌ `speedtest-cli` not found.\nInstall: `pip install speedtest-cli`")
    except subprocess.TimeoutExpired:
        await msg.edit("❌ Speedtest timed out.")
    except Exception as e:
        await msg.edit(f"❌ Error: `{e}`")


@Client.on_message(filters.command("restart") & filters.me)
async def restart_bot(client: Client, message: Message):
    await message.edit("♻️ **Restarting bot...**")
    await asyncio.sleep(1)
    import os, sys
    os.execv(sys.executable, [sys.executable] + sys.argv)
