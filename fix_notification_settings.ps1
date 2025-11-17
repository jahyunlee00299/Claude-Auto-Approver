# Fix Windows notification settings
Write-Host "Checking Windows Notification Settings..." -ForegroundColor Cyan
Write-Host ""

# Check current settings
$notifPath = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Notifications\Settings"

Write-Host "Current Notification Settings:" -ForegroundColor Yellow
Get-ItemProperty -Path $notifPath -ErrorAction SilentlyContinue | Format-List

Write-Host ""
Write-Host "Opening Windows Notification Settings..." -ForegroundColor Green
Start-Process "ms-settings:notifications"

Write-Host ""
Write-Host "Please check the following:" -ForegroundColor Yellow
Write-Host "  1. Notifications = ON" -ForegroundColor White
Write-Host "  2. 'Show notification banners' = ON" -ForegroundColor White
Write-Host "  3. 'Play a sound when a notification arrives' = ON" -ForegroundColor White
Write-Host "  4. Scroll down and find 'Python' or 'WindowsPowerShell'" -ForegroundColor White
Write-Host "  5. Make sure notifications are enabled for that app" -ForegroundColor White
Write-Host ""
Write-Host "Also check Focus Assist:" -ForegroundColor Yellow
Write-Host "  1. Press Win+A to open Action Center" -ForegroundColor White
Write-Host "  2. Click 'Focus assist'" -ForegroundColor White
Write-Host "  3. Set to 'Off' (not 'Priority only' or 'Alarms only')" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter when done checking settings"
