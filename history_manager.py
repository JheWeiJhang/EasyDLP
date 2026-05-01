import json
from datetime import datetime
from pathlib import Path

CONFIG_DIR = Path.home() / ".yt-dlp-gui"
HISTORY_FILE = CONFIG_DIR / "history.json"
MAX_ENTRIES = 500


class HistoryManager:
    def __init__(self):
        self._entries = []
        self.load()

    def load(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        if HISTORY_FILE.exists():
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    self._entries = json.load(f)
            except (json.JSONDecodeError, OSError):
                self._entries = []

    def save(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self._entries[-MAX_ENTRIES:], f, ensure_ascii=False, indent=2)

    def add(self, url: str, title: str, fmt: str, output_path: str, success: bool):
        entry = {
            "url": url,
            "title": title or url,
            "format": fmt,
            "output_path": output_path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "status": "成功" if success else "失敗",
        }
        self._entries.append(entry)
        self.save()
        return entry

    def get_all(self):
        return list(reversed(self._entries))

    def clear(self):
        self._entries = []
        self.save()
