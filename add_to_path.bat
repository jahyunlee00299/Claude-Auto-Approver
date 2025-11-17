@echo off
echo Adding Claude-Auto-Approver to PATH...
echo.

set "APPROVER_PATH=C:\Users\Jahyun\PycharmProjects\Claude-Auto-Approver"

:: Check if already in PATH
echo %PATH% | findstr /i /c:"%APPROVER_PATH%" >nul
if %errorlevel% equ 0 (
    echo Already in PATH!
    echo Current PATH includes: %APPROVER_PATH%
    pause
    exit /b 0
)

:: Add to User PATH (persistent)
echo Adding to User PATH...
for /f "skip=2 tokens=3*" %%a in ('reg query HKCU\Environment /v PATH 2^>nul') do set "CurrentPath=%%b"

if defined CurrentPath (
    setx PATH "%CurrentPath%;%APPROVER_PATH%"
) else (
    setx PATH "%APPROVER_PATH%"
)

if %errorlevel% equ 0 (
    echo.
    echo ============================================
    echo SUCCESS! Added to PATH:
    echo %APPROVER_PATH%
    echo ============================================
    echo.
    echo Please RESTART your CMD window for changes to take effect.
    echo.
    echo After restart, you can run these commands from anywhere:
    echo   - start_ocr_approver
    echo   - stop_ocr_approver
    echo   - restart_ocr_approver
    echo.
) else (
    echo.
    echo ERROR: Failed to add to PATH.
    echo Please run this batch file as Administrator.
    echo.
)

pause
