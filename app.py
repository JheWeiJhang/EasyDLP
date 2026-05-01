import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from downloader import Downloader
from history_manager import HistoryManager
from settings_manager import SettingsManager
import ffmpeg_manager
import ytdlp_manager

APP_TITLE = "EasyDLP"
WIN_W, WIN_H = 900, 640
SIDEBAR_W = 140
MODES = ["最佳畫質", "1080p", "720p", "480p", "僅音訊"]
AUDIO_FMTS = ["MP3", "AAC", "OPUS", "FLAC", "M4A"]


# ═══════════════════════════════════════════════════════════════════════ #
#  Download page                                                          #
# ═══════════════════════════════════════════════════════════════════════ #

class DownloadFrame(ctk.CTkFrame):
    def __init__(self, master, settings: SettingsManager, history: HistoryManager,
                 on_history_changed):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self._settings = settings
        self._history = history
        self._on_history_changed = on_history_changed
        self._downloading = False
        self._downloader: Downloader | None = None

        self.columnconfigure(0, weight=1)
        self._build_ui()

    # ------------------------------------------------------------------ #
    #  Build                                                               #
    # ------------------------------------------------------------------ #

    def _build_ui(self):
        pad = {"padx": 20, "pady": (8, 0)}

        # ── URL ──────────────────────────────────────────────────────── #
        ctk.CTkLabel(self, text="影片 / 播放清單 URL", font=ctk.CTkFont(size=13, weight="bold")
                     ).grid(row=0, column=0, sticky="w", **pad)

        url_row = ctk.CTkFrame(self, fg_color="transparent")
        url_row.grid(row=1, column=0, sticky="ew", padx=20, pady=(4, 0))
        url_row.columnconfigure(0, weight=1)

        self._url_var = tk.StringVar()
        self._url_entry = ctk.CTkEntry(url_row, textvariable=self._url_var,
                                       placeholder_text="https://www.youtube.com/watch?v=…",
                                       height=36, font=ctk.CTkFont(size=13))
        self._url_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(url_row, text="貼上", width=60, height=36,
                      command=self._paste_url).grid(row=0, column=1)

        # ── Format ───────────────────────────────────────────────────── #
        opt_frame = ctk.CTkFrame(self, fg_color="transparent")
        opt_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(16, 0))
        opt_frame.columnconfigure(1, weight=1)
        opt_frame.columnconfigure(3, weight=1)

        ctk.CTkLabel(opt_frame, text="下載模式", anchor="w").grid(row=0, column=0, sticky="w")
        self._mode_var = tk.StringVar(value=self._settings.get("default_mode"))
        self._mode_menu = ctk.CTkOptionMenu(
            opt_frame, variable=self._mode_var, values=MODES,
            command=self._on_mode_change, width=160)
        self._mode_menu.grid(row=0, column=1, sticky="w", padx=(10, 30))

        self._audio_label = ctk.CTkLabel(opt_frame, text="音訊格式", anchor="w")
        self._audio_label.grid(row=0, column=2, sticky="w")
        self._audio_var = tk.StringVar(value=self._settings.get("default_audio_fmt"))
        self._audio_menu = ctk.CTkOptionMenu(
            opt_frame, variable=self._audio_var, values=AUDIO_FMTS, width=120)
        self._audio_menu.grid(row=0, column=3, sticky="w", padx=(10, 0))
        self._on_mode_change(self._mode_var.get())

        # ── Checkboxes ───────────────────────────────────────────────── #
        chk_frame = ctk.CTkFrame(self, fg_color="transparent")
        chk_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(12, 0))

        self._subs_var = tk.BooleanVar(value=self._settings.get("subtitles"))
        ctk.CTkCheckBox(chk_frame, text="下載字幕", variable=self._subs_var,
                        command=self._on_subs_change).pack(side="left")

        self._langs_entry = ctk.CTkEntry(chk_frame, width=140,
                                         placeholder_text="語言 e.g. zh-TW,en")
        self._langs_entry.insert(0, self._settings.get("subtitle_langs"))
        self._langs_entry.pack(side="left", padx=(10, 20))
        self._on_subs_change()

        self._thumb_var = tk.BooleanVar(value=self._settings.get("embed_thumbnail"))
        ctk.CTkCheckBox(chk_frame, text="嵌入縮圖", variable=self._thumb_var).pack(side="left")

        # ── ffmpeg 狀態列（自動偵測，使用者不需要做任何事）──────────── #
        ffmpeg_frame = ctk.CTkFrame(self, fg_color="transparent")
        ffmpeg_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(6, 0))

        has_ffmpeg = ffmpeg_manager.is_available()
        ffmpeg_icon  = "✅" if has_ffmpeg else "⚠️"
        ffmpeg_text  = "影音自動合併為 MP4" if has_ffmpeg else "ffmpeg 未就緒，將下載單一串流"
        ffmpeg_color = ("gray40", "gray60") if has_ffmpeg else ("gray50", "gray50")

        ctk.CTkLabel(ffmpeg_frame,
                     text=f"{ffmpeg_icon}  {ffmpeg_text}",
                     font=ctk.CTkFont(size=11),
                     text_color=ffmpeg_color,
                     anchor="w").pack(side="left")

        # ── Output dir ───────────────────────────────────────────────── #
        ctk.CTkLabel(self, text="輸出目錄", font=ctk.CTkFont(size=13, weight="bold")
                     ).grid(row=5, column=0, sticky="w", padx=20, pady=(16, 0))

        dir_row = ctk.CTkFrame(self, fg_color="transparent")
        dir_row.grid(row=6, column=0, sticky="ew", padx=20, pady=(4, 0))
        dir_row.columnconfigure(0, weight=1)

        self._dir_var = tk.StringVar(value=self._settings.get("output_dir"))
        ctk.CTkEntry(dir_row, textvariable=self._dir_var, height=34,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(dir_row, text="瀏覽", width=60, height=34,
                      command=self._browse_dir).grid(row=0, column=1)

        # ── Download button ───────────────────────────────────────────── #
        self._dl_btn = ctk.CTkButton(
            self, text="▶  開始下載", height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            command=self._toggle_download)
        self._dl_btn.grid(row=7, column=0, sticky="ew", padx=20, pady=(20, 0))

        # ── Progress ─────────────────────────────────────────────────── #
        prog_frame = ctk.CTkFrame(self, fg_color="transparent")
        prog_frame.grid(row=8, column=0, sticky="ew", padx=20, pady=(12, 0))
        prog_frame.columnconfigure(0, weight=1)

        self._progress_bar = ctk.CTkProgressBar(prog_frame, height=14)
        self._progress_bar.set(0)
        self._progress_bar.grid(row=0, column=0, sticky="ew", padx=(0, 12))

        self._pct_label = ctk.CTkLabel(prog_frame, text="0%", width=40, anchor="e")
        self._pct_label.grid(row=0, column=1)

        self._info_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                        text_color="gray")
        self._info_label.grid(row=9, column=0, sticky="w", padx=20, pady=(2, 0))

        # ── Log ──────────────────────────────────────────────────────── #
        ctk.CTkLabel(self, text="輸出記錄", font=ctk.CTkFont(size=12, weight="bold")
                     ).grid(row=10, column=0, sticky="w", padx=20, pady=(14, 0))

        self._log_box = ctk.CTkTextbox(self, height=180, font=ctk.CTkFont(family="Consolas", size=11),
                                       wrap="none", state="disabled")
        self._log_box.grid(row=11, column=0, sticky="nsew", padx=20, pady=(4, 16))
        self.rowconfigure(11, weight=1)

    # ------------------------------------------------------------------ #
    #  Callbacks                                                           #
    # ------------------------------------------------------------------ #

    def _on_mode_change(self, value):
        is_audio = value == "僅音訊"
        state = "normal" if is_audio else "disabled"
        self._audio_label.configure(text_color="white" if is_audio else "gray")
        self._audio_menu.configure(state=state)

    def _on_subs_change(self):
        state = "normal" if self._subs_var.get() else "disabled"
        self._langs_entry.configure(state=state)

    def _paste_url(self):
        try:
            text = self.clipboard_get()
            self._url_var.set(text.strip())
        except tk.TclError:
            pass

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self._dir_var.get() or str(Path.home()))
        if d:
            self._dir_var.set(d)

    def _toggle_download(self):
        if self._downloading:
            self._cancel_download()
        else:
            self._start_download()

    def _start_download(self):
        url = self._url_var.get().strip()
        if not url.startswith("http"):
            self._log("請輸入有效的 URL（以 http 或 https 開頭）")
            return

        self._downloading = True
        self._dl_btn.configure(text="⏹  取消下載", fg_color="#c0392b",
                                hover_color="#922b21")
        self._progress_bar.set(0)
        self._pct_label.configure(text="0%")
        self._info_label.configure(text="")
        self._clear_log()

        options = {
            "mode": self._mode_var.get(),
            "audio_fmt": self._audio_var.get(),
            "subtitles": self._subs_var.get(),
            "subtitle_langs": self._langs_entry.get(),
            "embed_thumbnail": self._thumb_var.get(),
            "output_dir": self._dir_var.get(),
            "ytdlp_path": self._settings.get("ytdlp_path"),
        }
        self._current_url = url
        self._current_options = options

        self._downloader = Downloader(
            progress_cb=self._on_progress,
            log_cb=self._on_log,
            done_cb=self._on_done,
        )
        self._downloader.download(url, options)

    def _cancel_download(self):
        if self._downloader:
            self._downloader.cancel()

    # ── Thread callbacks (called from worker thread) ──────────────────── #

    def _on_progress(self, pct: float, speed: str, eta: str):
        self.after(0, self._update_progress, pct, speed, eta)

    def _on_log(self, line: str):
        self.after(0, self._log, line)

    def _on_done(self, success: bool, title: str, output_path: str, options: dict):
        self.after(0, self._finish, success, title, output_path, options)

    # ── Main-thread UI updates ────────────────────────────────────────── #

    def _update_progress(self, pct: float, speed: str, eta: str):
        self._progress_bar.set(pct / 100)
        self._pct_label.configure(text=f"{pct:.1f}%")
        info_parts = []
        if speed:
            info_parts.append(f"速度：{speed}")
        if eta:
            info_parts.append(f"剩餘：{eta}")
        self._info_label.configure(text="   ".join(info_parts))

    def _finish(self, success: bool, title: str, output_path: str, options: dict):
        self._downloading = False
        self._dl_btn.configure(text="▶  開始下載", fg_color=["#3B8ED0", "#1F6AA5"],
                                hover_color=["#36719F", "#144870"])
        if success:
            self._progress_bar.set(1)
            self._pct_label.configure(text="100%")
            self._info_label.configure(text="下載完成 ✓")
        else:
            self._info_label.configure(text="下載失敗或已取消")

        # Save to history
        fmt_label = options.get("mode", "")
        if fmt_label == "僅音訊":
            fmt_label = f"音訊 ({options.get('audio_fmt', '')})"
        self._history.add(
            url=self._current_url,
            title=title,
            fmt=fmt_label,
            output_path=output_path,
            success=success,
        )
        self._on_history_changed()

        # Persist current settings
        self._settings.set("default_mode", options.get("mode"))
        self._settings.set("default_audio_fmt", options.get("audio_fmt"))
        self._settings.set("subtitles", options.get("subtitles"))
        self._settings.set("subtitle_langs", options.get("subtitle_langs"))
        self._settings.set("embed_thumbnail", options.get("embed_thumbnail"))
        self._settings.set("output_dir", options.get("output_dir"))
        self._settings.save()

    def _log(self, text: str):
        self._log_box.configure(state="normal")
        self._log_box.insert("end", text + "\n")
        self._log_box.see("end")
        self._log_box.configure(state="disabled")

    def _clear_log(self):
        self._log_box.configure(state="normal")
        self._log_box.delete("1.0", "end")
        self._log_box.configure(state="disabled")


# ═══════════════════════════════════════════════════════════════════════ #
#  History page                                                           #
# ═══════════════════════════════════════════════════════════════════════ #

class HistoryFrame(ctk.CTkFrame):
    def __init__(self, master, history: HistoryManager):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self._history = history
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=20, pady=(14, 6))
        header.columnconfigure(0, weight=1)
        ctk.CTkLabel(header, text="下載記錄", font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header, text="清除記錄", width=80, height=28,
                      fg_color="#c0392b", hover_color="#922b21",
                      command=self._clear).grid(row=0, column=1, sticky="e")

        self._scroll = ctk.CTkScrollableFrame(self, label_text="")
        self._scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 16))
        self._scroll.columnconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        for w in self._scroll.winfo_children():
            w.destroy()

        entries = self._history.get_all()
        if not entries:
            ctk.CTkLabel(self._scroll, text="尚無下載記錄",
                         text_color="gray").pack(pady=40)
            return

        for i, entry in enumerate(entries):
            self._add_card(i, entry)

    def _add_card(self, idx: int, entry: dict):
        card = ctk.CTkFrame(self._scroll, corner_radius=8)
        card.grid(row=idx, column=0, sticky="ew", pady=4)
        card.columnconfigure(0, weight=1)

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.grid(row=0, column=0, columnspan=2, sticky="ew", padx=12, pady=(10, 2))
        top.columnconfigure(0, weight=1)

        title = entry.get("title") or entry.get("url", "")
        if len(title) > 70:
            title = title[:67] + "…"
        ctk.CTkLabel(top, text=title, font=ctk.CTkFont(size=13, weight="bold"),
                     anchor="w").grid(row=0, column=0, sticky="ew")

        status = entry.get("status", "")
        color = "#27ae60" if status == "成功" else "#c0392b"
        ctk.CTkLabel(top, text=status, text_color=color,
                     font=ctk.CTkFont(size=12)).grid(row=0, column=1, sticky="e")

        meta = f"{entry.get('format', '')}  ·  {entry.get('timestamp', '')}"
        ctk.CTkLabel(card, text=meta, text_color="gray", font=ctk.CTkFont(size=11),
                     anchor="w").grid(row=1, column=0, sticky="w", padx=12)

        url_short = entry.get("url", "")
        if len(url_short) > 60:
            url_short = url_short[:57] + "…"
        ctk.CTkLabel(card, text=url_short, text_color="gray", font=ctk.CTkFont(size=10),
                     anchor="w").grid(row=2, column=0, sticky="w", padx=12, pady=(0, 8))

        output_path = entry.get("output_path", "")
        if output_path:
            folder = str(Path(output_path).parent)
            ctk.CTkButton(card, text="開啟資料夾", width=90, height=26,
                          command=lambda p=folder: self._open_folder(p)
                          ).grid(row=2, column=1, padx=12, pady=(0, 8))

    def _clear(self):
        self._history.clear()
        self.refresh()

    def _open_folder(self, path: str):
        try:
            os.startfile(path)
        except Exception:
            pass


# ═══════════════════════════════════════════════════════════════════════ #
#  Settings page                                                          #
# ═══════════════════════════════════════════════════════════════════════ #

class SettingsFrame(ctk.CTkFrame):
    def __init__(self, master, settings: SettingsManager):
        super().__init__(master, corner_radius=0, fg_color="transparent")
        self._settings = settings
        self.columnconfigure(1, weight=1)
        self._build_ui()

    def _build_ui(self):
        pad = {"padx": (20, 20), "pady": (14, 0)}

        ctk.CTkLabel(self, text="設定", font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, columnspan=2, sticky="w", **pad)

        # Theme
        ctk.CTkLabel(self, text="外觀主題", anchor="w").grid(
            row=1, column=0, sticky="w", padx=(20, 10), pady=(20, 0))
        self._theme_var = tk.StringVar(value="深色" if self._settings.get("theme") == "dark" else "淡色")
        ctk.CTkSegmentedButton(self, values=["深色", "淡色"],
                               variable=self._theme_var,
                               command=self._on_theme_change
                               ).grid(row=1, column=1, sticky="w", pady=(20, 0))

        # Default output dir
        ctk.CTkLabel(self, text="預設輸出目錄", anchor="w").grid(
            row=2, column=0, sticky="w", padx=(20, 10), pady=(16, 0))
        dir_row = ctk.CTkFrame(self, fg_color="transparent")
        dir_row.grid(row=2, column=1, sticky="ew", pady=(16, 0), padx=(0, 20))
        dir_row.columnconfigure(0, weight=1)
        self._dir_var = tk.StringVar(value=self._settings.get("output_dir"))
        ctk.CTkEntry(dir_row, textvariable=self._dir_var, height=32).grid(
            row=0, column=0, sticky="ew", padx=(0, 8))
        ctk.CTkButton(dir_row, text="瀏覽", width=60, height=32,
                      command=self._browse_dir).grid(row=0, column=1)

        # Default mode
        ctk.CTkLabel(self, text="預設下載模式", anchor="w").grid(
            row=3, column=0, sticky="w", padx=(20, 10), pady=(16, 0))
        self._mode_var = tk.StringVar(value=self._settings.get("default_mode"))
        ctk.CTkOptionMenu(self, variable=self._mode_var, values=MODES, width=160
                          ).grid(row=3, column=1, sticky="w", pady=(16, 0))

        # yt-dlp path
        ctk.CTkLabel(self, text="yt-dlp 路徑\n（留空使用預設）", anchor="w",
                     justify="left").grid(row=4, column=0, sticky="w", padx=(20, 10), pady=(16, 0))
        self._ytdlp_var = tk.StringVar(value=self._settings.get("ytdlp_path"))
        ctk.CTkEntry(self, textvariable=self._ytdlp_var, height=32,
                     placeholder_text="yt-dlp  （或完整路徑）"
                     ).grid(row=4, column=1, sticky="ew", padx=(0, 20), pady=(16, 0))

        # Save button
        ctk.CTkButton(self, text="儲存設定", width=120, height=36,
                      command=self._save).grid(row=5, column=1, sticky="w",
                                               pady=(24, 0), padx=(0, 20))

        self._status_label = ctk.CTkLabel(self, text="", text_color="gray",
                                          font=ctk.CTkFont(size=11))
        self._status_label.grid(row=6, column=1, sticky="w", pady=(6, 0))

    def _on_theme_change(self, value):
        mode = "dark" if value == "深色" else "light"
        ctk.set_appearance_mode(mode)
        self._settings.set("theme", mode)
        self._settings.save()

    def _browse_dir(self):
        d = filedialog.askdirectory(initialdir=self._dir_var.get() or str(Path.home()))
        if d:
            self._dir_var.set(d)

    def _save(self):
        self._settings.set("output_dir", self._dir_var.get())
        self._settings.set("default_mode", self._mode_var.get())
        self._settings.set("ytdlp_path", self._ytdlp_var.get())
        self._settings.save()
        self._status_label.configure(text="已儲存 ✓")
        self.after(2000, lambda: self._status_label.configure(text=""))


# ═══════════════════════════════════════════════════════════════════════ #
#  Main App                                                               #
# ═══════════════════════════════════════════════════════════════════════ #

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(f"{WIN_W}x{WIN_H}")
        self.minsize(760, 520)

        self._settings = SettingsManager()
        self._history = HistoryManager()

        ctk.set_appearance_mode(self._settings.get("theme"))

        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

        self._build_sidebar()
        self._build_content()

        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._show_page("download")

        # Check yt-dlp availability after window is ready
        self.after(300, self._check_ytdlp)

    # ------------------------------------------------------------------ #
    #  Sidebar                                                             #
    # ------------------------------------------------------------------ #

    def _build_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=SIDEBAR_W, corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="nsew")
        sidebar.rowconfigure(10, weight=1)

        ctk.CTkLabel(sidebar, text="yt-dlp\nGUI",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     justify="center").pack(pady=(28, 24))

        self._nav_btns: dict[str, ctk.CTkButton] = {}
        for key, label in [("download", "⬇  下載"), ("history", "📋  記錄"), ("settings", "⚙  設定")]:
            btn = ctk.CTkButton(sidebar, text=label, width=SIDEBAR_W - 20,
                                height=40, anchor="w",
                                fg_color="transparent", hover_color=("gray75", "gray28"),
                                text_color=("gray10", "gray90"),
                                command=lambda k=key: self._show_page(k))
            btn.pack(padx=10, pady=4)
            self._nav_btns[key] = btn

    # ------------------------------------------------------------------ #
    #  Content area                                                        #
    # ------------------------------------------------------------------ #

    def _build_content(self):
        container = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        container.grid(row=0, column=1, sticky="nsew")
        container.columnconfigure(0, weight=1)
        container.rowconfigure(0, weight=1)

        self._pages: dict[str, ctk.CTkFrame] = {
            "download": DownloadFrame(container, self._settings, self._history,
                                      self._on_history_changed),
            "history": HistoryFrame(container, self._history),
            "settings": SettingsFrame(container, self._settings),
        }
        for page in self._pages.values():
            page.grid(row=0, column=0, sticky="nsew")

    def _show_page(self, key: str):
        for k, btn in self._nav_btns.items():
            if k == key:
                btn.configure(fg_color=("gray70", "gray30"))
            else:
                btn.configure(fg_color="transparent")
        self._pages[key].tkraise()

    # ------------------------------------------------------------------ #
    #  yt-dlp availability check & auto-download                          #
    # ------------------------------------------------------------------ #

    def _check_ytdlp(self):
        user_path = self._settings.get("ytdlp_path")
        if ytdlp_manager.any_ytdlp_available(user_path):
            return
        # Nothing found — show the download dialog
        YtdlpDownloadDialog(self, on_done=self._on_ytdlp_downloaded)

    def _on_ytdlp_downloaded(self, success: bool):
        if success:
            dl_page: DownloadFrame = self._pages["download"]
            dl_page._log("yt-dlp 已就緒，可以開始下載。")

    # ------------------------------------------------------------------ #
    #  Inter-page events                                                   #
    # ------------------------------------------------------------------ #

    def _on_history_changed(self):
        self._pages["history"].refresh()

    # ------------------------------------------------------------------ #
    #  Window close                                                        #
    # ------------------------------------------------------------------ #

    def _on_close(self):
        self._settings.save()
        self.destroy()


# ═══════════════════════════════════════════════════════════════════════ #
#  yt-dlp auto-download dialog                                            #
# ═══════════════════════════════════════════════════════════════════════ #

class YtdlpDownloadDialog(ctk.CTkToplevel):
    """Shown on first launch when no yt-dlp binary is found anywhere."""

    def __init__(self, master, on_done=None):
        super().__init__(master)
        self.title("下載 yt-dlp")
        self.geometry("440x260")
        self.resizable(False, False)
        self.grab_set()
        self.lift()

        self._on_done = on_done
        self._downloading = False

        self.columnconfigure(0, weight=1)

        ctk.CTkLabel(self, text="找不到 yt-dlp",
                     font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, pady=(24, 6))

        ctk.CTkLabel(
            self,
            text="系統上找不到可用的 yt-dlp。\n點擊下方按鈕自動從 GitHub 下載最新版本。",
            justify="center",
        ).grid(row=1, column=0, padx=20)

        self._progress_bar = ctk.CTkProgressBar(self, width=380)
        self._progress_bar.set(0)
        self._progress_bar.grid(row=2, column=0, padx=30, pady=(20, 4))

        self._status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=11),
                                           text_color="gray")
        self._status_label.grid(row=3, column=0)

        self._dl_btn = ctk.CTkButton(self, text="自動下載 yt-dlp", width=180, height=38,
                                      command=self._start_download)
        self._dl_btn.grid(row=4, column=0, pady=(16, 8))

        ctk.CTkButton(self, text="略過", width=80, height=32,
                      fg_color="transparent", border_width=1,
                      command=self._skip).grid(row=5, column=0, pady=(0, 16))

    def _start_download(self):
        if self._downloading:
            return
        self._downloading = True
        self._dl_btn.configure(state="disabled", text="下載中…")

        ytdlp_manager.download_exe_async(
            progress_cb=self._on_progress,
            log_cb=self._on_log,
            done_cb=self._on_done_inner,
        )

    def _on_progress(self, pct: float):
        self.after(0, self._update_progress, pct)

    def _on_log(self, msg: str):
        self.after(0, self._status_label.configure, {"text": msg[:60]})

    def _update_progress(self, pct: float):
        self._progress_bar.set(pct / 100)
        self._status_label.configure(text=f"{pct:.1f}%")

    def _on_done_inner(self, success: bool, detail: str):
        self.after(0, self._finish, success, detail)

    def _finish(self, success: bool, detail: str):
        if success:
            self._progress_bar.set(1)
            self._status_label.configure(text="下載完成 ✓")
            self.after(1200, self.destroy)
        else:
            self._status_label.configure(text=f"失敗：{detail[:50]}")
            self._dl_btn.configure(state="normal", text="重試")
            self._downloading = False

        if self._on_done:
            self._on_done(success)

    def _skip(self):
        self.destroy()
