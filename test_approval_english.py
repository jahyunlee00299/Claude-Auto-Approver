#!/usr/bin/env python3
"""
Test script to show approval notification in English
"""
import time
import subprocess
import random

def show_approval_notification():
    """
    Show an approval notification using PowerShell toast
    """
    try:
        # Add timestamp
        timestamp = time.strftime('%H:%M:%S')

        # Random approval messages for variety
        messages = [
            ("Auto Approval Complete", "Claude Code request approved successfully"),
            ("Request Approved", "Your action has been automatically approved"),
            ("Permission Granted", "The requested operation was approved"),
            ("Approval Success", "Action approved at " + timestamp),
        ]

        title, message = random.choice(messages)
        title = f"{title} [{timestamp}]"

        print(f"[INFO] Showing notification: {title}")

        # PowerShell script for Windows Toast with sound
        ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'

$template = @"
<toast duration='long'>
    <visual>
        <binding template='ToastGeneric'>
            <text>{title}</text>
            <text>{message}</text>
            <text placement='attribution'>Claude Auto-Approver</text>
        </binding>
    </visual>
    <audio src='ms-winsoundevent:Notification.IM'/>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
'''

        # Execute PowerShell
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"[SUCCESS] Approval notification displayed!")
            print(f"           Title: {title}")
            print(f"           Message: {message}")
            print(f"           Sound: IM notification sound")
        else:
            print(f"[ERROR] PowerShell error: {result.stderr}")

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Notification command timed out (notification may still appear)")
    except Exception as e:
        print(f"[ERROR] Failed to show notification: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("Approval Message Test")
    print("=" * 60)
    print()

    # Show multiple notifications with delay
    for i in range(3):
        print(f"\n[Notification {i+1}/3]")
        show_approval_notification()
        if i < 2:
            print("Waiting 2 seconds before next notification...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("[INFO] Check Windows Action Center for notifications!")
    print("[TIP] If no notifications appear, check:")
    print("      - Windows Focus Assist settings")
    print("      - Notification settings for PowerShell")
    print("      - Do Not Disturb mode")
    print("=" * 60)