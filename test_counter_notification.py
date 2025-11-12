#!/usr/bin/env python3
"""
Windows notification with counter display
"""
import time
import subprocess
import winsound

def show_approval_notification_with_counter(approval_count=1):
    """
    Show Windows notification with counter in title
    """
    try:
        timestamp = time.strftime('%H:%M:%S')
        # Add counter badge-like display in title
        title = f"[{approval_count}] Auto Approval - {timestamp}"
        message = f"Claude Code request approved\\nTotal approvals: {approval_count}"

        print(f"[INFO] Showing notification #{approval_count}")
        print(f"       Title: {title}")
        print(f"       Message: {message}")

        # Play notification sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # PowerShell script for toast notification
        ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'

# Create toast with counter in visual
$template = @"
<toast scenario='reminder' duration='long'>
    <visual>
        <binding template='ToastGeneric'>
            <text hint-style='header'>{title}</text>
            <text hint-style='body'>Claude Code request approved</text>
            <text hint-style='captionSubtle'>Total approvals: {approval_count}</text>
            <group>
                <subgroup hint-weight='33'>
                    <text hint-style='base' hint-align='center'>{approval_count}</text>
                    <text hint-style='captionSubtle' hint-align='center'>Count</text>
                </subgroup>
                <subgroup hint-weight='67'>
                    <text hint-style='captionSubtle'>Auto-approved at {timestamp}</text>
                    <text hint-style='captionSubtle'>Window: Claude-Auto-Approver</text>
                </subgroup>
            </group>
        </binding>
    </visual>
    <audio src='ms-winsoundevent:Notification.IM'/>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
$toast.Tag = "approval_{approval_count}"
$toast.Group = "approvals"
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
            print(f"[SUCCESS] Notification #{approval_count} displayed!")
            return True
        else:
            # Even if there's an error, notification might still show
            if "ToastNotification" in result.stderr:
                print(f"[WARNING] Minor error but notification likely shown")
                return True
            else:
                print(f"[ERROR] Failed to show notification")
                return False

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Notification command timed out (notification may still appear)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to show notification: {e}")
        return False

def main():
    print("=" * 70)
    print(" Windows Notification with Counter Display Test")
    print("=" * 70)
    print()
    print("This will show 5 notifications with increasing counter numbers")
    print()

    # Show multiple notifications with increasing counter
    total_approvals = 0

    for i in range(5):
        total_approvals += 1
        print(f"\n{'='*50}")
        print(f"Notification {i+1} of 5")
        print(f"{'='*50}")

        success = show_approval_notification_with_counter(total_approvals)

        if success:
            print(f"  [OK] Notification with counter [{total_approvals}] sent")
        else:
            print(f"  [FAIL] Failed to send notification")

        if i < 4:
            print("\n  Waiting 2 seconds before next notification...")
            time.sleep(2)

    print("\n" + "=" * 70)
    print(" TEST COMPLETED")
    print("=" * 70)
    print()
    print("Check Windows Notification Center (Win+N) for:")
    print()
    print("  - 5 notifications with counters [1] through [5] in titles")
    print("  - Each showing 'Total approvals: X' in the message")
    print("  - Timestamps for each approval")
    print()
    print("The counter number appears in square brackets [X] in each")
    print("notification title, similar to a badge indicator.")
    print()
    print("If notifications don't appear:")
    print("  - Check Windows Settings > System > Notifications")
    print("  - Turn off Focus Assist / Do Not Disturb")
    print("  - Check PowerShell notification permissions")
    print("=" * 70)

if __name__ == "__main__":
    main()