# yt-dlp GUI

> 一個現代化的 yt-dlp 圖形介面，讓任何人都能輕鬆下載網路影片，無需學習指令列操作。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ 功能特色

| 功能 | 說明 |
|------|------|
| 🎬 影片下載 | 支援 YouTube、TikTok、Instagram、Twitter 等 1000+ 個網站 |
| 🎵 音訊提取 | 直接下載 MP3、AAC、OPUS、FLAC、M4A |
| 📺 畫質選擇 | 最佳畫質 / 1080p / 720p / 480p |
| 🔀 自動合併 | 自動合併影音串流為單一 MP4（內建 ffmpeg，無需安裝） |
| 📝 字幕下載 | 支援手動與自動字幕，可指定語言 |
| 🖼️ 縮圖嵌入 | 自動嵌入影片封面圖片 |
| 📋 下載記錄 | 完整記錄所有下載歷史，附快速開啟資料夾功能 |
| ⚙️ 設定保存 | 記住上次的下載目錄與偏好設定 |
| 🌙 深色主題 | 現代深色/淡色主題切換 |
| 📦 首次自動下載 | 若系統無 yt-dlp，自動從 GitHub 抓取最新版本 |

---

## 🚀 快速開始

### 方法一：直接執行（需要 Python）

1. 安裝 Python 3.10 或更新版本：https://www.python.org/downloads/
2. 安裝依賴：
   ```bash
   pip install customtkinter Pillow imageio-ffmpeg
   ```
3. 雙擊 **`main.pyw`** 或執行 **`啟動.bat`**

### 方法二：打包成獨立 exe（不需要 Python）

1. 雙擊 **`build_exe.bat`**
2. 等待 2~5 分鐘自動完成打包
3. 執行檔位置：`dist/yt-dlp GUI/yt-dlp GUI.exe`
4. 將整個 `dist/yt-dlp GUI/` 資料夾複製給任何 Windows 使用者即可

---

## 📸 介面截圖

### 下載頁面
- 貼上 URL → 選擇畫質 → 點擊下載
- 即時顯示下載進度、速度與剩餘時間

### 記錄頁面
- 查看所有下載歷史
- 一鍵開啟下載檔案所在資料夾

### 設定頁面
- 切換深色/淡色主題
- 設定預設下載目錄
- 自訂 yt-dlp 執行檔路徑

---

## 📂 專案結構

```
gui_youtubedl/
├── main.py              # 程式入口（有 console 視窗）
├── main.pyw             # 程式入口（無 console 視窗，雙擊用）
├── app.py               # 主視窗 UI（CustomTkinter）
├── downloader.py        # yt-dlp subprocess 封裝
├── ffmpeg_manager.py    # ffmpeg 自動偵測（使用 imageio-ffmpeg）
├── ytdlp_manager.py     # yt-dlp 自動下載管理
├── history_manager.py   # 下載記錄（JSON 持久化）
├── settings_manager.py  # 使用者設定（JSON 持久化）
├── requirements.txt     # Python 依賴清單
├── build_exe.bat        # PyInstaller 一鍵打包腳本
└── 啟動.bat             # 快速啟動腳本
```

---

## 🔧 系統需求

| 需求 | 說明 |
|------|------|
| 作業系統 | Windows 10 / 11 |
| Python | 3.10 或更新版本（打包成 exe 後不需要） |
| 網路 | 需要網路連線下載影片 |
| ffmpeg | **不需要手動安裝**，已透過 `imageio-ffmpeg` 內建 |
| yt-dlp | **不需要手動安裝**，首次執行時自動從 GitHub 下載 |

---

## 📦 Python 依賴

```
customtkinter>=5.2.2   # 現代化 GUI 框架
Pillow>=10.0.0         # 圖片處理
imageio-ffmpeg>=0.5.1  # 內建 ffmpeg 二進位檔
```

---

## 🛠️ 技術說明

### yt-dlp 整合方式
程式透過 `subprocess` 呼叫 yt-dlp，優先順序如下：
1. 使用者在設定中指定的自訂路徑
2. 自動下載的本地 exe（`bin/yt-dlp.exe`）
3. 本地 yt-dlp 原始碼目錄（`../youtubedl/`）
4. 系統 PATH 中的 `yt-dlp` 指令

### ffmpeg 整合方式
使用 `imageio-ffmpeg` 套件提供的內建 ffmpeg 二進位檔，使用者完全不需要手動安裝 ffmpeg。打包成 exe 時，ffmpeg 也一併內嵌。

### 設定與記錄儲存位置
- 設定檔：`~/.yt-dlp-gui/settings.json`
- 下載記錄：`~/.yt-dlp-gui/history.json`

---

## 📋 支援的網站

透過 yt-dlp 支援超過 **1000 個網站**，包含：
YouTube、TikTok、Instagram、Twitter / X、Facebook、Twitch、Bilibili、NicoNico、Reddit、SoundCloud 等

完整清單請參考：[yt-dlp 支援網站列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## 📄 授權

本專案採用 [MIT License](LICENSE)。

本專案使用以下開源工具：
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Unlicense
- [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) - MIT
- [imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) - BSD 2-Clause
- [Pillow](https://github.com/python-pillow/Pillow) - HPND

---

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

1. Fork 此 repo
2. 建立功能分支：`git checkout -b feature/your-feature`
3. Commit 修改：`git commit -m 'Add some feature'`
4. Push 到分支：`git push origin feature/your-feature`
5. 開啟 Pull Request
