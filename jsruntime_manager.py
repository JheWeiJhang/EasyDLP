"""
Detects a JavaScript runtime (Node.js / Deno) that yt-dlp can use
to solve YouTube's n-challenge, which prevents download throttling.

Without a JS runtime, some YouTube CDN servers throttle downloads
to ~5 KiB/s. With Node.js installed, yt-dlp solves the challenge
and achieves full speed.
"""

import shutil
from functools import lru_cache

# Runtimes supported by yt-dlp, in preference order
_CANDIDATES = [
    ("node",   "Node.js"),
    ("nodejs", "Node.js"),
    ("deno",   "Deno"),
]

NODEJS_DOWNLOAD_URL = "https://nodejs.org/en/download"


@lru_cache(maxsize=1)
def find_jsruntime() -> tuple[str, str] | None:
    """Return (executable, display_name) of the first found runtime, or None."""
    for exe, name in _CANDIDATES:
        if shutil.which(exe):
            return exe, name
    return None


def is_available() -> bool:
    return find_jsruntime() is not None


def get_ytdlp_args() -> list[str]:
    """Return ['--js-runtimes', 'node'] if a runtime is found, else []."""
    rt = find_jsruntime()
    return ["--js-runtimes", rt[0]] if rt else []


def status_text() -> str:
    rt = find_jsruntime()
    if rt:
        return f"✅ JS Runtime：{rt[1]}（YouTube 全速下載）"
    return "⚠️ 未安裝 Node.js（部分 YouTube 影片可能較慢）"
