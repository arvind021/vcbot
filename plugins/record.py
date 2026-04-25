"""
Record Plugin
/startrecord - Start Recording VC
/stoprecord  - Stop & Upload the recording
"""

import os
import time
from pyrogram import Client, filters
from pyrogram.types import Message
from state import state

RECORD_DIR = "recordings"
os.makedirs(RECORD_DIR, exist_ok=True)


@Client.on_message(filters.command("startrecord") & filters.me)
async def start_record(client: Client, message: Message):
    if not state.group_id:
        return await message.edit("❌ Set group first: `/setgroup [id]`")
    if state.is_recording:
        return await message.edit("⚠️ Already recording!")

    state.is_recording = True
    state._record_start = time.time()
    state._record_file = os.path.join(RECORD_DIR, f"record_{int(time.time())}.ogg")

    await message.edit(
        f"🔴 **Recording Started!**\n"
        f"Group: `{state.group_id}`\n"
        f"File: `{state._record_file}`\n"
        f"Use `/stoprecord` to stop and upload."
    )
    # Note: Actual recording requires pytgcalls RecordStream
    # from pytgcalls.types import RecordStream
    # await vc.start_recording(group_id, RecordStream(state._record_file))


@Client.on_message(filters.command("stoprecord") & filters.me)
async def stop_record(client: Client, message: Message):
    if not state.is_recording:
        return await message.edit("❌ Not recording.")

    state.is_recording = False
    duration = round(time.time() - getattr(state, "_record_start", time.time()), 1)
    record_file = getattr(state, "_record_file", None)

    msg = await message.edit(f"⏹ Recording stopped. Duration: `{duration}s`\n⬆️ Uploading...")

    try:
        if record_file and os.path.exists(record_file):
            await client.send_audio(
                message.chat.id,
                record_file,
                caption=f"🎙️ VC Recording\n⏱ Duration: `{duration}s`\n📁 File: `{os.path.basename(record_file)}`",
            )
            await msg.edit("✅ Recording uploaded!")
        else:
            await msg.edit(
                f"⏹ Stopped. Duration: `{duration}s`\n"
                f"_Recording file not found (pytgcalls RecordStream needed for actual recording)._"
            )
    except Exception as e:
        await msg.edit(f"❌ Upload error: `{e}`")
