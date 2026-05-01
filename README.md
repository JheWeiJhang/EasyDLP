# EasyDLP

> 一個非官方的第三方圖形介面，讓任何人都能輕鬆使用 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 下載網路影片，無需學習指令列操作。

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![Platform](https://img.shields.io/badge/Platform-Windows-blue?logo=windows)
![License](https://img.shields.io/badge/License-MIT-green)

> [!IMPORTANT]
> **本專案為非官方第三方工具，與 yt-dlp 專案、其開發者及任何影音平台無任何關聯。**
> EasyDLP 本身不包含任何下載功能，核心下載能力完全由 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 提供。

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

### 方法一：下載已打包的 exe（最簡單，不需要任何安裝）

1. 前往 [Releases 頁面](https://github.com/JheWeiJhang/EasyDLP/releases/latest)
2. 下載 `EasyDLP-vX.X.X-windows-x64.zip`
3. 解壓縮後雙擊 **`EasyDLP.exe`** 即可使用

### 方法二：從原始碼執行（需要 Python 3.10+）

```bash
git clone https://github.com/JheWeiJhang/EasyDLP.git
cd EasyDLP
pip install -r requirements.txt
python main.pyw
```

### 方法三：自行打包成 exe

```
雙擊 build_exe.bat，等待 2~5 分鐘
完成後執行 dist/EasyDLP/EasyDLP.exe
```

---

## 🔧 系統需求

| 需求 | 說明 |
|------|------|
| 作業系統 | Windows 10 / 11 |
| Python | 3.10 或更新版本（使用打包 exe 時不需要） |
| 網路 | 需要網路連線下載影片 |
| yt-dlp | **不需要手動安裝**，首次執行時自動從 GitHub 下載 |
| ffmpeg | **不需要手動安裝**，已透過 `imageio-ffmpeg` 內建 |

---

## 📂 專案結構

```
EasyDLP/
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

## 📦 Python 依賴

```
customtkinter>=5.2.2   # 現代化 GUI 框架
Pillow>=10.0.0         # 圖片處理
imageio-ffmpeg>=0.5.1  # 內建 ffmpeg 二進位檔
```

---

## ⚖️ 授權與第三方歸屬

### EasyDLP 本身

本專案採用 **[MIT License](LICENSE)**。

---

### 使用的第三方工具與授權

EasyDLP 在執行時會下載並使用以下第三方工具。**這些工具的著作權屬於各自的開發者，EasyDLP 不對這些工具的行為負責。**

| 工具 | 用途 | 授權 | 來源 |
|------|------|------|------|
| **yt-dlp** | 核心下載引擎 | [Unlicense](https://github.com/yt-dlp/yt-dlp/blob/master/LICENSE)（公共領域） | [github.com/yt-dlp/yt-dlp](https://github.com/yt-dlp/yt-dlp) |
| **FFmpeg** | 影音合併／轉碼 | [LGPL v2.1+](https://ffmpeg.org/legal.html) | [ffmpeg.org](https://ffmpeg.org)，由 imageio-ffmpeg 提供 |
| **imageio-ffmpeg** | 內建 ffmpeg 二進位 | [BSD 2-Clause](https://github.com/imageio/imageio-ffmpeg/blob/master/LICENSE) | [github.com/imageio/imageio-ffmpeg](https://github.com/imageio/imageio-ffmpeg) |
| **CustomTkinter** | GUI 框架 | [MIT](https://github.com/TomSchimansky/CustomTkinter/blob/master/LICENSE) | [github.com/TomSchimansky/CustomTkinter](https://github.com/TomSchimansky/CustomTkinter) |
| **Pillow** | 圖片處理 | [HPND](https://github.com/python-pillow/Pillow/blob/main/LICENSE) | [github.com/python-pillow/Pillow](https://github.com/python-pillow/Pillow) |

#### FFmpeg LGPL 合規說明

本程式透過 `imageio-ffmpeg` 使用 FFmpeg（LGPL v2.1+）。依照 LGPL 規範：

- 使用者可在「設定」頁面自行指定替換版本的 ffmpeg 執行檔路徑
- FFmpeg 原始碼可於 [ffmpeg.org](https://ffmpeg.org/download.html) 取得
- imageio-ffmpeg 所使用的 ffmpeg 建置來源：[BtbN/FFmpeg-Builds](https://github.com/BtbN/FFmpeg-Builds)

---

## ⚠️ 法律免責聲明

1. **非官方工具**：EasyDLP 與 yt-dlp 專案、YouTube、TikTok、Instagram 或任何其他影音平台**無任何官方關聯**。

2. **用途責任**：下載影片前請確認您有合法權利這樣做。在許多國家和地區，未經授權下載受版權保護的內容可能違反：
   - 平台的服務條款（Terms of Service）
   - 著作權法（Copyright Law）

3. **個人使用**：本工具僅供學術研究、個人備份等合法用途。

4. **免責**：本專案開發者對使用者透過本工具進行的任何下載行為所造成的法律責任不承擔責任。

---

## 📋 支援的網站

透過 yt-dlp 支援超過 **1000 個網站**，完整清單請參考：
[yt-dlp 支援網站列表](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md)

---

## 🤝 貢獻

歡迎提交 Issue 或 Pull Request！

1. Fork 此 repo
2. 建立功能分支：`git checkout -b feature/your-feature`
3. Commit 修改：`git commit -m 'Add some feature'`
4. Push 到分支：`git push origin feature/your-feature`
5. 開啟 Pull Request
