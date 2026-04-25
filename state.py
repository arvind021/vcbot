"""
Global state manager - stores runtime settings and shared objects
"""

class State:
    # Shared pytgcalls instance (set in bot.py)
    vc = None

    # Current group call settings
    group_id: int = 0
    join_as: int = 0
    volume: int = 100
    pitch: float = 1.0
    echo_enabled: bool = False
    echo_params: dict = {}

    # Queue of audio file paths to play
    queue: list = []
    current_audio: str = None
    is_paused: bool = False
    is_playing: bool = False

    # Live forwarding
    live_active: bool = False
    live_source: int = 0
    live_dest: int = 0
    source_volume: int = 100
    source_pitch: float = 1.0
    source_echo: bool = False
    dest_volume: int = 100
    dest_pitch: float = 1.0
    dest_echo: bool = False

    # Record
    is_recording: bool = False
    _record_start: float = 0.0
    _record_file: str = ""

    # Downloaded audios {name: filepath}
    downloaded_audios: dict = {}

    # Remote kernel
    record_vc_joined: bool = False
    play_vc_joined: bool = False


state = State()
