import os

class Config:
    # ============ REQUIRED ============
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    SESSION_STRING = os.environ.get("SESSION_STRING", "")

    # ============ OPTIONAL ============
    # Your Telegram User ID (for owner-only commands)
    OWNER_ID = int(os.environ.get("OWNER_ID", 0))

    # Default group where bot plays audio
    GROUP_ID = int(os.environ.get("GROUP_ID", 0))

    # Join voice chat as this channel/user
    JOIN_AS = int(os.environ.get("JOIN_AS", 0))  # 0 = join as self

    # Default volume (1-200)
    DEFAULT_VOLUME = int(os.environ.get("DEFAULT_VOLUME", 100))
