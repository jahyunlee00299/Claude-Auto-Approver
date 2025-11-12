#!/usr/bin/env python3
"""
Claude Auto Approver - Windows Notification Module
"""
import time
import subprocess
import winsound
import os

def show_claude_approval_notification(approval_count=1, window_title="Unknown"):
    """
    Show Windows notification with Claude Auto Approver branding
    """
    try:
        timestamp = time.strftime('%H:%M:%S')

        # Create notification content
        notification_title = f"Auto Approval [{timestamp}]"
        notification_body = f"Window: {window_title[:30]}"
        notification_subtitle = f"Total approvals: {approval_count}"

        print(f"[INFO] Sending notification #{approval_count}")
        print(f"       Title: {notification_title}")
        print(f"       Window: {window_title}")

        # Play notification sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # PowerShell script for Windows Toast Notification
        # Using a custom APP_ID for "Claude Auto Approver"
        ps_script = f'''
# Load required assemblies
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

# Custom APP_ID for Claude Auto Approver
$APP_ID = 'Claude.Auto.Approver'

# Try to register the app if not already registered
try {{
    $appReg = Get-StartApps | Where-Object {{$_.AppID -eq $APP_ID}}
    if (-not $appReg) {{
        # Use PowerShell as fallback but with custom display name
        $APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'
    }}
}} catch {{
    $APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'
}}

# Create the toast notification XML
$template = @"
<toast scenario='reminder' duration='long'>
    <visual>
        <binding template='ToastGeneric'>
            <text hint-style='header'>{notification_title}</text>
            <text hint-style='body'>{notification_body}</text>
            <text hint-style='captionSubtle'>{notification_subtitle}</text>
            <text placement='attribution'>Claude Auto Approver</text>
        </binding>
    </visual>
    <audio src='ms-winsoundevent:Notification.IM'/>
</toast>
"@

# Load and show the notification
$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
$toast.Tag = "approval_{approval_count}"
$toast.Group = "ClaudeAutoApprover"
$toast.ExpirationTime = [DateTimeOffset]::Now.AddMinutes(5)

# Create notifier and show
$notifier = [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID)
$notifier.Show($toast)
'''

        # Execute PowerShell command
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"[SUCCESS] Notification sent to Windows Action Center")
            return True
        else:
            # Even with errors, notification might still show
            print(f"[WARNING] PowerShell returned error but notification may still appear")
            return True

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Notification command timed out (notification may still appear)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to show notification: {e}")
        return False

def test_notifications():
    """
    Test function to show sample notifications
    """
    print("=" * 60)
    print("Claude Auto Approver - Notification Test")
    print("=" * 60)
    print()

    test_windows = [
        "PowerShell - Admin",
        "Git Bash - Claude-Auto-Approver",
        "Python Console",
        "Command Prompt",
        "VS Code - main.py"
    ]

    for i, window in enumerate(test_windows, 1):
        print(f"\n[Test {i}/5]")
        show_claude_approval_notification(i, window)

        if i < len(test_windows):
            print("  Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("Test Complete!")
    print()
    print("Check Windows Action Center for notifications")
    print("All should appear under 'Claude Auto Approver'")
    print("=" * 60)

if __name__ == "__main__":
    test_notifications()