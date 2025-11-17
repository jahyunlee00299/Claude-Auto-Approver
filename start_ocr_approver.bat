@echo off
cd /d "C:\Users\Jahyun\PycharmProjects\Claude-Auto-Approver"
echo Starting OCR Auto Approver...
start /min pythonw.exe ocr_auto_approver.py
echo Started! Running in background.
timeout /t 2 /nobreak >nul
