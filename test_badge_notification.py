#!/usr/bin/env python3
"""
Enhanced Windows notification with badge support
"""
import time
import subprocess
import winsound

def show_approval_notification_with_badge(approval_count=1):
    """
    Show Windows notification with badge counter
    """
    try:
        timestamp = time.strftime('%H:%M:%S')
        title = f"Auto Approval [{timestamp}]"
        message = f"Claude Code request approved (Total: {approval_count})"

        print(f"[INFO] Showing notification: {title}")
        print(f"       Message: {message}")
        print(f"       Badge count: {approval_count}")

        # Play notification sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # PowerShell script with badge support
        ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'

# Create toast with badge value
$template = @"
<toast scenario='reminder' duration='long'>
    <visual>
        <binding template='ToastGeneric'>
            <text hint-style='header'>{title}</text>
            <text hint-style='body'>{message}</text>
            <text placement='attribution'>Claude Auto-Approver</text>
            <image placement='appLogoOverride' src='https://www.microsoft.com/favicon.ico'/>
        </binding>
    </visual>
    <audio src='ms-winsoundevent:Notification.IM'/>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
$toast.Tag = "approval_${{Get-Random}}"
$toast.Group = "approvals"
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)

# Update badge with count
$badgeXml = @"
<badge value='{approval_count}'/>
"@

$badgeDoc = New-Object Windows.Data.Xml.Dom.XmlDocument
$badgeDoc.LoadXml($badgeXml)
$badge = [Windows.UI.Notifications.BadgeNotification]::new($badgeDoc)
[Windows.UI.Notifications.BadgeNotificationManager]::CreateBadgeUpdaterForApplication($APP_ID).Update($badge)
'''

        # Execute PowerShell
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            print(f"[SUCCESS] Notification and badge displayed!")
            return True
        else:
            print(f"[ERROR] PowerShell error: {result.stderr}")
            return False

    except subprocess.TimeoutExpired:
        print(f"[WARNING] Notification command timed out (notification may still appear)")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to show notification: {e}")
        return False

def clear_badge():
    """
    Clear the badge counter
    """
    try:
        ps_script = '''
[Windows.UI.Notifications.BadgeNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
$APP_ID = '{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe'
[Windows.UI.Notifications.BadgeNotificationManager]::CreateBadgeUpdaterForApplication($APP_ID).Clear()
'''
        subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            timeout=2
        )
        print("[INFO] Badge counter cleared")
    except:
        pass

def main():
    print("=" * 60)
    print("Windows Notification + Badge Test")
    print("=" * 60)
    print()

    # Clear any existing badges
    clear_badge()

    # Show multiple notifications with increasing badge count
    total_approvals = 0

    for i in range(5):
        total_approvals += 1
        print(f"\n[Notification {i+1}/5] Approval count: {total_approvals}")

        success = show_approval_notification_with_badge(total_approvals)

        if success:
            print(f"  -> Number '{total_approvals}' displayed in notification center and badge")
        else:
            print(f"  -> Notification failed")

        if i < 4:
            print("  Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("[COMPLETED] Test finished!")
    print()
    print("Check for:")
    print("  1. 5 notifications in Windows notification center")
    print("  2. Number badge on PowerShell taskbar icon")
    print("  3. Notification sounds playing")
    print()
    print("[TIP] If notifications don't appear:")
    print("  - Check Windows Settings > System > Notifications")
    print("  - Turn off Focus Assist")
    print("  - Check PowerShell notification permissions")
    print("=" * 60)

    # Wait before clearing badge
    print("\nClearing badge in 10 seconds...")
    time.sleep(10)
    clear_badge()
    print("[INFO] Badge cleared")

if __name__ == "__main__":
    main()