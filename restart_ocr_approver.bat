@echo off
echo Restarting OCR Auto Approver...
call stop_ocr_approver.bat
timeout /t 1 /nobreak >nul
call start_ocr_approver.bat
echo Restarted!
