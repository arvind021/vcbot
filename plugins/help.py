"""
Help Plugin - /vchelp
"""

from pyrogram import Client, filters
from pyrogram.types import Message

HELP_TEXT = """
🎙️ **Voice Chat Userbot — Commands**

━━━━━━━━━━━━━━━━━━━━
👥 **Multi-Group Management:**
━━━━━━━━━━━━━━━━━━━━
➕ `/setgroup -1001xxx [Name]` — Group add/save karo
🗑 `/removegroup -1001xxx` — Group remove karo
📋 `/listgroups` — Sab saved groups dekho
⚙️ `/groupsettings -1001xxx` — Group ki settings dekho
▶️ `/playgroup -1001xxx` — Is group mein play karo

🔊 `/groupvolume -1001xxx 100` — Group ka volume
🎼 `/grouppitch -1001xxx 1.0` — Group ka pitch
🎚 `/groupecho -1001xxx on` — Group ka echo
🙊 `/groupjoinas -1001xxx -100yyy` — Group ka join-as

━━━━━━━━━━━━━━━━━━━━
▶️ **Play Commands:**
━━━━━━━━━━━━━━━━━━━━
🙊 `/setjoinas [ChannelId]` — VC join via channel
🔊 `/volume [1-200]` — Active group ka volume
🎼 `/pitch [float]` — Active group ka pitch
🎚 `/echo on|off` — Echo toggle
✅ `/skip` — Skip current audio
⚠️ `/stop` — Stop + clear queue
💫 `/pause` — Pause
⚡️ `/resume` — Resume
🍄 `/leavegroup` — Leave VC

━━━━━━━━━━━━━━━━━━━━
📡 **Live Forwarding:**
━━━━━━━━━━━━━━━━━━━━
📡 `/golive [src] [dest]` — VC-to-VC forward start
⏹ `/stoplive` — Stop live
📊 `/livestatus` — Live status
🔄 `/updatelive` — Settings update
🔊 `/sourcevolume` `/destvolume` — Volume
🎼 `/sourcepitch` `/destpitch` — Pitch
🎚 `/sourceecho` `/destecho` — Echo

━━━━━━━━━━━━━━━━━━━━
📂 **Downloaded Audios:**
━━━━━━━━━━━━━━━━━━━━
⬇️ `/download [name]` — Reply karke download
🎵 `/audio [name.ogg]` — Play downloaded audio

━━━━━━━━━━━━━━━━━━━━
🖥️ **Remote Kernel:**
━━━━━━━━━━━━━━━━━━━━
🔗 `/join` `/leave` `/leaveall`
🎤 `/leaverecord` `/leaveplay`

━━━━━━━━━━━━━━━━━━━━
🔊 **Audio Controls:**
━━━━━━━━━━━━━━━━━━━━
🔊 `/level [1-25]` | 🎚 `/bass [0-15]`
🔇 `/mute` | 🔈 `/unmute`

━━━━━━━━━━━━━━━━━━━━
🎙️ **Record & Utils:**
━━━━━━━━━━━━━━━━━━━━
🔴 `/startrecord` | ⏹ `/stoprecord`
📺 `/screenshare` | 📴 `/screenshareoff`
⚡ `/speedtest` | ♻️ `/restart`
📋 `/vchelp` — Yeh help
"""


@Client.on_message(filters.command("vchelp") & filters.me)
async def vchelp(client: Client, message: Message):
    await message.edit(HELP_TEXT, disable_web_page_preview=True)
