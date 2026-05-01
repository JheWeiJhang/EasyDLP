"""
Manages a local node.exe for yt-dlp's n-challenge solver.

Without Node.js, YouTube throttles DASH stream downloads to ~5 KiB/s
because yt-dlp cannot solve the n-challenge (JS-based URL obfuscation).

Priority order:
  1. bin/node.exe  ← auto-downloaded here
  2. System 'node' command
"""

import json
import shutil
import subprocess
import threading
import urllib.request
import zipfile
from pathlib import Path

NODEJS_INDEX_API = "https://nodejs.org/dist/index.json"
BIN_DIR = Path(__file__).parent / "bin"
LOCAL_NODE = BIN_DIR / "node.exe"


# ------------------------------------------------------------------ #
#  Detection                                                           #
# ------------------------------------------------------------------ #

def find_node() -> str | None:
    """Return path to node.exe, or None."""
    if LOCAL_NODE.exists():
        return str(LOCAL_NODE)
    return shutil.which("node") or shutil.which("nodejs")


def is_available() -> bool:
    return find_node() is not None


def get_ytdlp_args() -> list[str]:
    """Return ['--js-runtimes', 'node:PATH'] if available, else []."""
    path = find_node()
    if path:
        # yt-dlp accepts RUNTIME[:PATH] format
        return ["--js-runtimes", f"node:{path}"]
    return []


def get_local_version() -> str:
    path = find_node()
    if not path:
        return ""
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip()
    except Exception:
        return ""


def status_text() -> str:
    if is_available():
        ver = get_local_version()
        return f"✅ Node.js {ver}（YouTube 全速下載）"
    return "⚠️ Node.js 未就緒（YouTube 下載可能較慢）"


# ------------------------------------------------------------------ #
#  Download                                                            #
# ------------------------------------------------------------------ #

def _get_latest_lts_info() -> tuple[str, str]:
    """Return (version, zip_url) for the latest Node.js LTS (Windows x64)."""
    req = urllib.request.Request(
        NODEJS_INDEX_API,
        headers={"User-Agent": "EasyDLP/1.0 (https://github.com/JheWeiJhang/EasyDLP)"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        versions = json.loads(resp.read())

    for v in versions:
        if v.get("lts"):
            ver = v["version"]  # e.g. "v20.19.0"
            zip_url = (
                f"https://nodejs.org/dist/{ver}"
                f"/node-{ver}-win-x64.zip"
            )
            return ver, zip_url

    raise RuntimeError("無法從 Node.js API 取得 LTS 版本資訊")


def download_node(progress_cb=None, log_cb=None) -> Path:
    """
    Download Node.js LTS and extract node.exe into bin/.
    progress_cb(pct: float)  — 0.0–100.0
    log_cb(msg: str)
    Returns path to node.exe.
    """
    def log(msg):
        if log_cb:
            log_cb(msg)

    BIN_DIR.mkdir(parents=True, exist_ok=True)
    zip_tmp = BIN_DIR / "node_lts.zip"

    log("正在取得 Node.js LTS 版本資訊…")
    version, zip_url = _get_latest_lts_info()
    log(f"最新 LTS：{version}，開始下載（約 20~25 MB）…")

    def reporthook(block_num, block_size, total_size):
        if total_size > 0 and progress_cb:
            pct = min(block_num * block_size / total_size * 100, 100.0)
            progress_cb(pct)

    urllib.request.urlretrieve(zip_url, zip_tmp, reporthook)

    log("正在解壓縮 node.exe…")
    with zipfile.ZipFile(zip_tmp) as zf:
        # node.exe 在 zip 內的路徑是 "node-vX.Y.Z-win-x64/node.exe"
        node_entry = next(
            (n for n in zf.namelist() if n.endswith("/node.exe") or n == "node.exe"),
            None,
        )
        if not node_entry:
            raise RuntimeError("在 Node.js zip 中找不到 node.exe")
        LOCAL_NODE.write_bytes(zf.read(node_entry))

    zip_tmp.unlink(missing_ok=True)
    log(f"Node.js {version} 已安裝至 {LOCAL_NODE}")
    return LOCAL_NODE


# ------------------------------------------------------------------ #
#  Async helper                                                        #
# ------------------------------------------------------------------ #

def download_node_async(progress_cb=None, log_cb=None, done_cb=None):
    """Run download_node in a daemon thread."""
    def _run():
        try:
            path = download_node(progress_cb=progress_cb, log_cb=log_cb)
            if done_cb:
                done_cb(True, str(path))
        except Exception as e:
            if log_cb:
                log_cb(f"下載失敗：{e}")
            if done_cb:
                done_cb(False, str(e))

    t = threading.Thread(target=_run, daemon=True)
    t.start()
