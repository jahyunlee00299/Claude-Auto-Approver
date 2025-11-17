#!/usr/bin/env python3
"""Test notification using PowerShell fallback"""
import subprocess
import time

def test_powershell_notification():
    """Test PowerShell-based notification"""
    print("="*60)
    print("PowerShell Notification Test")
    print("="*60)
    print()

    title = "Claude Auto Approver - PowerShell Test"
    message = "This is a test notification using PowerShell.\n\nIf you see this, PowerShell notifications work!"

    # Escape special characters
    title_escaped = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    message_escaped = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'

$template = @"
<toast scenario='reminder' duration='long'>
    <visual>
        <binding template='ToastGeneric'>
            <text hint-style='header'>{title_escaped}</text>
            <text hint-style='body'>{message_escaped}</text>
            <text placement='attribution'>Claude Auto Approver</text>
        </binding>
    </visual>
    <audio src='ms-winsoundevent:Notification.SMS'/>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
$toast.Tag = "test_notification"
$toast.Group = "ClaudeAutoApprover"
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)

Write-Host "Notification sent via PowerShell!"
'''

    print("[TEST] Sending PowerShell notification...")
    try:
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=10
        )

        print(f"[INFO] PowerShell output: {result.stdout}")
        if result.stderr:
            print(f"[WARNING] PowerShell errors: {result.stderr}")

        print("[SUCCESS] PowerShell notification sent!")
        print("[INFO] Check Windows Action Center or look for a toast popup")

        time.sleep(3)
        return True

    except Exception as e:
        print(f"[ERROR] PowerShell notification failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_powershell_notification()
