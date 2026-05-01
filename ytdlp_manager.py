"""
Manages a local yt-dlp.exe binary.

Priority order (highest → lowest):
  1. User-specified path (settings)
  2. bin/yt-dlp.exe  ← auto-downloaded here
  3. Local source tree (python -m yt_dlp)
  4. System 'yt-dlp' command
"""

import shutil
import subprocess
import sys
import threading
import urllib.request
from pathlib import Path

GITHUB_API = "https://api.github.com/repos/yt-dlp/yt-dlp/releases/latest"
EXE_ASSET_NAME = "yt-dlp.exe"
BIN_DIR = Path(__file__).parent / "bin"
LOCAL_EXE = BIN_DIR / "yt-dlp.exe"
LOCAL_SOURCE = Path(__file__).parent.parent / "youtubedl" / "yt_dlp"


# ------------------------------------------------------------------ #
#  Detection                                                           #
# ------------------------------------------------------------------ #

def find_ytdlp(user_path: str = "") -> str | None:
    """Return the command/path to use, or None if nothing is available."""
    if user_path and Path(user_path).exists():
        return user_path
    if LOCAL_EXE.exists():
        return str(LOCAL_EXE)
    if LOCAL_SOURCE.is_dir():
        return None  # caller uses python -m yt_dlp
    if shutil.which("yt-dlp"):
        return "yt-dlp"
    return None


def any_ytdlp_available(user_path: str = "") -> bool:
    """True if *any* yt-dlp variant is usable right now."""
    if user_path and Path(user_path).exists():
        return True
    if LOCAL_EXE.exists():
        return True
    if LOCAL_SOURCE.is_dir():
        return True
    if shutil.which("yt-dlp"):
        return True
    return False


# ------------------------------------------------------------------ #
#  Download                                                            #
# ------------------------------------------------------------------ #

def fetch_latest_release_url() -> tuple[str, str]:
    """Return (download_url, version_tag) for the latest yt-dlp.exe."""
    import json
    req = urllib.request.Request(
        GITHUB_API,
        headers={"Accept": "application/vnd.github+json",
                 "User-Agent": "yt-dlp-gui/1.0"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())

    tag = data["tag_name"]
    for asset in data["assets"]:
        if asset["name"] == EXE_ASSET_NAME:
            return asset["browser_download_url"], tag

    raise RuntimeError(f"找不到 {EXE_ASSET_NAME} 於版本 {tag}")


def download_exe(progress_cb=None, log_cb=None) -> Path:
    """
    Download the latest yt-dlp.exe into bin/.
    progress_cb(pct: float)  — 0.0–100.0
    log_cb(msg: str)
    Returns the path to the downloaded exe.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    tmp = LOCAL_EXE.with_suffix(".tmp")

    log("正在從 GitHub 取得最新版本資訊…")
    url, tag = fetch_latest_release_url()
    log(f"最新版本：{tag}，開始下載…")

    def reporthook(block_num, block_size, total_size):
        if total_size > 0 and progress_cb:
            pct = min(block_num * block_size / total_size * 100, 100.0)
            progress_cb(pct)

    urllib.request.urlretrieve(url, tmp, reporthook)
    tmp.replace(LOCAL_EXE)
    log(f"yt-dlp {tag} 已下載至 {LOCAL_EXE}")
    return LOCAL_EXE


def get_local_version() -> str:
    """Return version string of the local exe, or '' if unavailable."""
    if not LOCAL_EXE.exists():
        return ""
    try:
        result = subprocess.run(
            [str(LOCAL_EXE), "--version"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""


# ------------------------------------------------------------------ #
#  Async helper                                                        #
# ------------------------------------------------------------------ #

def download_exe_async(progress_cb=None, log_cb=None, done_cb=None):
    """Run download_exe in a daemon thread."""
    def _run():
        try:
            path = download_exe(progress_cb=progress_cb, log_cb=log_cb)
            if done_cb:
                done_cb(True, str(path))
        except Exception as e:
            if log_cb:
                log_cb(f"下載失敗：{e}")
            if done_cb:
                done_cb(False, str(e))

    t = threading.Thread(target=_run, daemon=True)
    t.start()
