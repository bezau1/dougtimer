import os

# --- OBS WebSocket connection settings ---
# Fill these in to match your OBS "Tools > WebSocket Server Settings" panel.
# You can also set these as environment variables instead of hardcoding here,
# e.g.: export OBS_WS_PASSWORD="your_password_here"

OBS_WS_HOST = os.environ.get("OBS_WS_HOST", "localhost")
OBS_WS_PORT = int(os.environ.get("OBS_WS_PORT", "4455"))
OBS_WS_PASSWORD = os.environ.get("OBS_WS_PASSWORD", "INSERTPASSHERE")

# The scene your countdown timer / background sources live in.
# obscountdowntimer.py calls set_source_visibility("/// Countdown Timer", ...)
# so this must match that scene name exactly (including symbols/spaces).
DEFAULT_SCENE = "/// Countdown Timer"
