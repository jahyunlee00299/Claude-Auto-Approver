# Create startup shortcut for Claude Auto Approver
$WshShell = New-Object -comObject WScript.Shell
$StartupPath = [System.Environment]::GetFolderPath('Startup')
$ShortcutPath = Join-Path $StartupPath "Claude Auto Approver.lnk"
$TargetPath = Join-Path $PSScriptRoot "start_ocr_approver.bat"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = $TargetPath
$Shortcut.WorkingDirectory = $PSScriptRoot
$Shortcut.Description = "Claude Auto Approver - Auto-approve Claude Code prompts"
$Shortcut.Save()

Write-Host "Startup shortcut created at: $ShortcutPath"
Write-Host "Target: $TargetPath"
