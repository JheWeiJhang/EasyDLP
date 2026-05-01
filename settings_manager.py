import json
import os
from pathlib import Path

CONFIG_DIR = Path.home() / ".yt-dlp-gui"
SETTINGS_FILE = CONFIG_DIR / "settings.json"

DEFAULTS = {
    "output_dir": str(Path.home() / "Downloads"),
    "default_mode": "最佳畫質",
    "default_audio_fmt": "MP3",
    "subtitle_langs": "zh-TW,en",
    "embed_thumbnail": False,
    "subtitles": False,
    "merge": False,          # 預設不合併（不需要 ffmpeg）
    "theme": "dark",
    "ytdlp_path": "",
}


class SettingsManager:
    def __init__(self):
        self._data = dict(DEFAULTS)
        self.load()

    def load(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if SETTINGS_FILE.exists():
            try:
                with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                    saved = json.load(f)
                self._data.update(saved)
            except (json.JSONDecodeError, OSError):
                pass

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def get(self, key):
        return self._data.get(key, DEFAULTS.get(key))

    def set(self, key, value):
        self._data[key] = value
