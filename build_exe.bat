@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ============================================
echo   EasyDLP - 打包成獨立執行檔 (.exe)
echo ============================================
echo.

REM 檢查 Python
where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [錯誤] 找不到 Python，請先安裝 Python 3.10+
    pause & exit /b 1
)

REM 安裝所有依賴（包含 imageio-ffmpeg，內建 ffmpeg 二進位檔）
echo [1/3] 安裝依賴（customtkinter、Pillow、imageio-ffmpeg）...
pip install customtkinter Pillow imageio-ffmpeg --quiet
if %errorlevel% neq 0 (
    echo [錯誤] 安裝依賴失敗
    pause & exit /b 1
)

REM 安裝 PyInstaller
echo [2/3] 安裝 PyInstaller...
pip install pyinstaller --quiet
if %errorlevel% neq 0 (
    echo [錯誤] 安裝 PyInstaller 失敗
    pause & exit /b 1
)

REM 打包
echo [3/3] 開始打包（這可能需要 2~5 分鐘）...
echo       ffmpeg 將自動內嵌進 exe，使用者不需要另行安裝。
echo.
python -m PyInstaller ^
    --noconfirm ^
    --windowed ^
    --onedir ^
    --name "EasyDLP" ^
    --hidden-import customtkinter ^
    --hidden-import imageio_ffmpeg ^
    --collect-all customtkinter ^
    --collect-all imageio_ffmpeg ^
    --add-data "settings_manager.py;." ^
    --add-data "history_manager.py;." ^
    --add-data "downloader.py;." ^
    --add-data "ytdlp_manager.py;." ^
    --add-data "ffmpeg_manager.py;." ^
    main.pyw

if %errorlevel% neq 0 (
    echo.
    echo [錯誤] 打包失敗，請檢查上方錯誤訊息。
    pause & exit /b 1
)

echo.
echo ============================================
echo   打包完成！
echo.
echo   執行檔位置：
echo     dist\EasyDLP\EasyDLP.exe
echo.
echo   此資料夾可直接複製給任何 Windows 使用者，
echo   不需要安裝 Python 或 ffmpeg。
echo ============================================
echo.

set /p open="是否開啟輸出資料夾？(Y/N): "
if /i "%open%"=="Y" explorer "dist\EasyDLP"

pause
