@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 嘗試用 pythonw（無 console 視窗）啟動
where pythonw >nul 2>&1
if %errorlevel%==0 (
    start "" pythonw "%~dp0main.pyw"
    exit /b
)

REM 備用：用一般 python 啟動
where python >nul 2>&1
if %errorlevel%==0 (
    start "" python "%~dp0main.py"
    exit /b
)

echo [錯誤] 找不到 Python，請先安裝 Python 3.10 以上版本。
echo 下載網址：https://www.python.org/downloads/
pause
