# -*- coding: utf-8 -*-
# .pyw 副檔名讓 Windows 用 pythonw.exe 執行，不會出現黑色 console 視窗
# 直接雙擊此檔即可啟動 GUI

import sys
import os

# 確保工作目錄是此腳本所在的資料夾（雙擊執行時路徑可能不對）
os.chdir(os.path.dirname(os.path.abspath(__file__)))

import customtkinter as ctk
from app import App

if __name__ == "__main__":
    ctk.set_default_color_theme("blue")
    app = App()
    app.mainloop()
