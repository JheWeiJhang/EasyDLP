import locale
import os
import re
import subprocess
import sys
import threading
from pathlib import Path

import ffmpeg_manager
import ytdlp_manager

_LOCAL_YTDLP = Path(__file__).parent.parent / "youtubedl"
_PROGRESS_RE = re.compile(r"\[download\]\s+([\d.]+)%")
_SPEED_RE    = re.compile(r"at\s+([\d.]+\s*\S+/s)")
_ETA_RE      = re.compile(r"ETA\s+([\d:]+)")
_DEST_RE     = re.compile(r"\[download\] Destination:\s*(.+)")
_MERGE_RE    = re.compile(r"\[Merger\] Merging formats into \"(.+)\"")

# ── 格式字串（有 ffmpeg → 分離串流取最高畫質後合併；無 ffmpeg → 單一預混串流） ── #
_FORMAT_WITH_FFMPEG = {
    "最佳畫質": "bestvideo+bestaudio/best",
    "1080p":   "bestvideo[height<=1080]+bestaudio/best[height<=1080]",
    "720p":    "bestvideo[height<=720]+bestaudio/best[height<=720]",
    "480p":    "bestvideo[height<=480]+bestaudio/best[height<=480]",
}
_FORMAT_NO_FFMPEG = {
    "最佳畫質": "best",
    "1080p":   "best[height<=1080]/best",
    "720p":    "best[height<=720]/best",
    "480p":    "best[height<=480]/best",
}

AUDIO_FORMAT_MAP = {
    "MP3": "mp3",
    "AAC": "aac",
    "OPUS": "opus",
    "FLAC": "flac",
    "M4A": "m4a",
}


def _build_ytdlp_base(ytdlp_path: str) -> list[str]:
    if ytdlp_path and Path(ytdlp_path).exists():
        return [ytdlp_path]
    if ytdlp_manager.LOCAL_EXE.exists():
        return [str(ytdlp_manager.LOCAL_EXE)]
    if (_LOCAL_YTDLP / "yt_dlp").is_dir():
        return [sys.executable, "-m", "yt_dlp", "--no-config-locations"]
    return ["yt-dlp"]


def _decode_line(raw: bytes) -> str:
    """
    將 yt-dlp stdout 的 raw bytes 解碼為 str。

    yt-dlp exe 在 Windows 上可能用 UTF-8 或系統 OEM 編碼（如 cp950）輸出，
    視其執行環境而定。策略：
      1. 先試 UTF-8（最常見，也是我們期望的）
      2. 失敗就用 locale.getpreferredencoding(False)（Windows ANSI / OEM，如 cp950）
      3. 最後保底用 'replace' 避免 crash
    """
    try:
        return raw.decode("utf-8").rstrip()
    except UnicodeDecodeError:
        pass
    sys_enc = locale.getpreferredencoding(False) or "cp950"
    return raw.decode(sys_enc, errors="replace").rstrip()


def _subprocess_env() -> dict:
    """強制 UTF-8 輸出，解決 Windows cp950 亂碼問題。"""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    return env


class Downloader:
    def __init__(self, progress_cb, log_cb, done_cb):
        self.progress_cb = progress_cb
        self.log_cb      = log_cb
        self.done_cb     = done_cb
        self._process: subprocess.Popen | None = None
        self._lock       = threading.Lock()
        self._cancelled  = False
        self._output_path = ""
        self._title       = ""

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #

    def download(self, url: str, options: dict):
        cmd = self._build_command(url, options)
        self._output_path = options.get("output_dir", "")
        self._title = ""
        self._cancelled = False
        t = threading.Thread(target=self._run, args=(cmd, options), daemon=True)
        t.start()

    def cancel(self):
        """終止下載：殺掉整個進程樹（含 ffmpeg 子進程與 SSL 重試連線）。"""
        self._cancelled = True
        with self._lock:
            proc = self._process
        if proc and proc.poll() is None:
            try:
                # taskkill /F /T 強制終止該 PID 及其所有子進程
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    capture_output=True,
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            except Exception:
                proc.kill()  # 備援：直接 kill

    # ------------------------------------------------------------------ #
    #  Command builder                                                     #
    # ------------------------------------------------------------------ #

    def _build_command(self, url: str, options: dict) -> list[str]:
        ytdlp_path = options.get("ytdlp_path", "")
        cmd = _build_ytdlp_base(ytdlp_path)

        mode      = options.get("mode", "最佳畫質")
        audio_fmt = options.get("audio_fmt", "MP3")
        ffmpeg    = ffmpeg_manager.get_ffmpeg_path()   # None 表示沒有 ffmpeg

        if mode == "僅音訊":
            # 音訊提取一定需要 ffmpeg；有的話用最高品質，沒有就跳過轉檔直接取 m4a/webm
            cmd += ["-x",
                    "--audio-format", AUDIO_FORMAT_MAP.get(audio_fmt, "mp3"),
                    "--audio-quality", "0"]
            if ffmpeg:
                cmd += ["--ffmpeg-location", ffmpeg]
        else:
            if ffmpeg:
                # 有 ffmpeg：取最高畫質分離串流，合併成 mp4
                fmt = _FORMAT_WITH_FFMPEG.get(mode, "bestvideo+bestaudio/best")
                cmd += ["-f", fmt,
                        "--merge-output-format", "mp4",
                        "--ffmpeg-location", ffmpeg]
            else:
                # 無 ffmpeg：取單一預混串流，不做合併
                fmt = _FORMAT_NO_FFMPEG.get(mode, "best")
                cmd += ["-f", fmt]

        # 輸出路徑
        output_dir = options.get("output_dir", ".")
        cmd += ["-o", f"{output_dir}/%(title)s.%(ext)s"]

        # 字幕
        if options.get("subtitles"):
            langs = options.get("subtitle_langs", "zh-TW,en").strip() or "zh-TW,en"
            cmd += ["--write-subs", "--write-auto-subs", "--sub-langs", langs]

        # 縮圖嵌入（需要 ffmpeg）
        if options.get("embed_thumbnail") and ffmpeg:
            cmd += ["--embed-thumbnail", "--ffmpeg-location", ffmpeg]

        # YouTube 專用：使用 tv_embedded + web player client
        # tv_embedded：不需要 JS runtime、不需要 GVS PO Token，可取得高畫質格式
        # android client 需要 PO Token，缺少時會被降到 format 18（360p 舊格式）並被 YouTube 限速
        cmd += ["--extractor-args", "youtube:player_client=tv_embedded,web"]

        # 進度輸出（機器可讀格式）
        cmd += ["--newline", "--progress"]

        cmd.append(url)
        return cmd

    # ------------------------------------------------------------------ #
    #  Runner                                                              #
    # ------------------------------------------------------------------ #

    def _run(self, cmd: list[str], options: dict):
        try:
            with self._lock:
                self._process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    # ★ 讀取 raw bytes，不指定 text/encoding
                    #   避免 yt-dlp exe 在 Windows 以 cp950 輸出時被誤判為 UTF-8
                    env=_subprocess_env(),
                    cwd=str(_LOCAL_YTDLP) if (_LOCAL_YTDLP / "yt_dlp").is_dir() else None,
                    # ★ 隱藏 Windows 黑色 console 視窗
                    creationflags=subprocess.CREATE_NO_WINDOW,
                )
            proc = self._process
            for raw in proc.stdout:
                if self._cancelled:
                    break
                line = _decode_line(raw)
                self._parse_line(line)
                self.log_cb(line)
            proc.wait()
            success = (proc.returncode == 0) and not self._cancelled
        except FileNotFoundError:
            self.log_cb("錯誤：找不到 yt-dlp 指令。請確認已安裝或在設定中指定路徑。")
            success = False
        except Exception as e:
            self.log_cb(f"錯誤：{e}")
            success = False

        self.done_cb(success, self._title, self._output_path, options)

    def _parse_line(self, line: str):
        # 優先抓合併後的最終路徑
        m2 = _MERGE_RE.search(line)
        if m2:
            self._output_path = m2.group(1).strip()
            self._title = Path(self._output_path).stem
            return

        # 下載中途的目的地（可能是中間檔）
        m = _DEST_RE.search(line)
        if m:
            path = m.group(1).strip()
            if not self._title:
                self._title = Path(path).stem
            self._output_path = path

        # 進度
        pm = _PROGRESS_RE.search(line)
        if pm:
            pct = float(pm.group(1))
            speed = sm.group(1) if (sm := _SPEED_RE.search(line)) else ""
            eta   = em.group(1) if (em := _ETA_RE.search(line))   else ""
            self.progress_cb(pct, speed, eta)
