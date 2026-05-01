"""
ffmpeg_manager.py
─────────────────
自動找到 ffmpeg 執行檔，優先使用 imageio-ffmpeg 內建版本。
使用者完全不需要手動安裝 ffmpeg。

偵測優先順序：
  1. imageio-ffmpeg 內建（pip install imageio-ffmpeg，PyInstaller 打包時自動帶入）
  2. 系統 PATH 裡的 ffmpeg
  3. 找不到 → 回傳 None（yt-dlp 退回單一檔案模式，不需要 ffmpeg）
"""

import shutil
from functools import lru_cache


@lru_cache(maxsize=1)
def get_ffmpeg_path() -> str | None:
    """
    回傳 ffmpeg 執行檔路徑。
    找不到時回傳 None（下載仍可繼續，但不會合併影音串流）。
    """
    # 1. imageio-ffmpeg 內建版本（最可靠，PyInstaller 可一起打包）
    try:
        import imageio_ffmpeg
        path = imageio_ffmpeg.get_ffmpeg_exe()
        if path:
            return path
    except (ImportError, RuntimeError):
        pass

    # 2. 系統 PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg

    return None


def is_available() -> bool:
    return get_ffmpeg_path() is not None


def status_text() -> str:
    path = get_ffmpeg_path()
    if path:
        return f"ffmpeg 已就緒"
    return "ffmpeg 未找到（將以單一串流下載）"
