@echo off
echo Stopping OCR Auto Approver...
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq ocr_auto_approver*" 2>nul
if %errorlevel% equ 0 (
    echo OCR Auto Approver stopped.
) else (
    echo Trying alternative method...
    taskkill /F /IM pythonw.exe 2>nul
    if %errorlevel% equ 0 (
        echo All pythonw.exe processes stopped.
    ) else (
        echo No OCR Auto Approver process found.
    )
)
timeout /t 2 /nobreak >nul
