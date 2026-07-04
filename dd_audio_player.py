"""
dd_audio_player.py

Minimal audio player wrapper using ffplay (part of ffmpeg), since it's
reliable across Linux distros without extra GTK/GStreamer dependencies
that packages like `playsound` often need.

Requires: ffmpeg installed (e.g. `sudo pacman -S ffmpeg` on Arch,
`sudo apt install ffmpeg` on Debian/Ubuntu).

Exposes the method obscountdowntimer.py calls:
    play_audio(filename, loop, block, ducking)

The three bool args match the original call site
(audio_manager.play_audio("bee.mp3", False, False, False)) — meaning was
never documented in the recovered script, so this implements the most
sensible guess: loop / block(wait for it to finish) / ducking(lower other
audio - not implemented, just accepted so the call doesn't crash).
"""

import shutil
import subprocess

_ffplay_path = shutil.which("ffplay")


class AudioManager:
    def __init__(self, audio_dir="."):
        self.audio_dir = audio_dir
        self._procs = []
        if _ffplay_path is None:
            print("[Audio] Warning: ffplay not found. Install ffmpeg to enable audio playback.")

    def play_audio(self, filename, loop=False, block=False, ducking=False):
        if _ffplay_path is None:
            print(f"[Audio] Skipped playing '{filename}' (ffplay not installed)")
            return

        path = filename if "/" in filename else f"{self.audio_dir}/{filename}"
        cmd = [_ffplay_path, "-nodisp", "-autoexit", "-loglevel", "quiet"]
        if loop:
            cmd += ["-loop", "0"]
        cmd.append(path)

        try:
            proc = subprocess.Popen(cmd)
            self._procs.append(proc)
            if block:
                proc.wait()
        except FileNotFoundError:
            print(f"[Audio] File not found: {path}")

    def stop_all(self):
        for proc in self._procs:
            if proc.poll() is None:
                proc.terminate()
        self._procs.clear()
