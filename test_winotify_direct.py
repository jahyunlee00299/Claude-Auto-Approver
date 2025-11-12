#!/usr/bin/env python3
"""
Direct test of winotify with all features
"""
import time
from winotify import Notification, audio

def show_winotify_notification(title, message, app_name="Claude Auto Approver"):
    """Show notification using winotify"""
    try:
        # Create notification
        toast = Notification(
            app_id=app_name,
            title=title,
            msg=message,
            duration="long",
            icon=""  # No icon for now
        )

        # Set sound
        toast.set_audio(audio.Default, loop=False)

        # Add launch action (optional)
        toast.launch = ""

        # Show the notification
        toast.show()

        print(f"[SUCCESS] Notification displayed: {title}")
        return True

    except Exception as e:
        print(f"[ERROR] Failed to show notification: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("Direct Winotify Test")
    print("=" * 60)
    print()

    # Test notifications
    notifications = [
        ("[1] Auto Approval", "PowerShell window detected", "Claude Auto Approver"),
        ("[2] Auto Approval", "Python console detected", "Claude Auto Approver"),
        ("[3] Auto Approval", "Command Prompt detected", "Claude Auto Approver"),
        ("[4] Auto Approval", "Git Bash detected", "Claude Auto Approver"),
        ("[5] Auto Approval", "VS Code detected", "Claude Auto Approver"),
    ]

    success_count = 0

    for i, (title, message, app_name) in enumerate(notifications, 1):
        timestamp = time.strftime('%H:%M:%S')
        full_title = f"{title} - {timestamp}"

        print(f"\n[Test {i}/5]")
        print(f"  App: {app_name}")
        print(f"  Title: {full_title}")
        print(f"  Message: {message}")

        success = show_winotify_notification(full_title, message, app_name)

        if success:
            success_count += 1
        else:
            print("  [FAIL] Could not show notification")

        if i < len(notifications):
            print("  Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print(f"Test Complete! {success_count}/5 notifications sent")
    print()

    if success_count == 0:
        print("No notifications were displayed. Possible issues:")
        print("  1. Windows Focus Assist is ON")
        print("  2. Notifications are disabled in Windows Settings")
        print("  3. Python.exe is blocked from sending notifications")
        print()
        print("To fix:")
        print("  1. Turn OFF Focus Assist (Win+N > Focus Assist)")
        print("  2. Settings > System > Notifications > Turn ON")
        print("  3. Allow Python.exe in notification settings")
    else:
        print("Check Windows Action Center for notifications")
        print("They should appear under 'Claude Auto Approver'")

    print("=" * 60)

if __name__ == "__main__":
    main()