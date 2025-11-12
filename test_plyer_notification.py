#!/usr/bin/env python3
"""
Windows Notification using Plyer library
"""
import time
from plyer import notification
import winsound

def show_plyer_notification(title, message, timeout=5):
    """
    Show Windows notification using plyer
    """
    try:
        # Play sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # Show notification
        notification.notify(
            title=title,
            message=message,
            app_name='Claude Auto-Approver',
            timeout=timeout
        )

        return True
    except Exception as e:
        print(f"[ERROR] Failed to show notification: {e}")
        return False

def main():
    print("=" * 60)
    print("Plyer Notification Test")
    print("=" * 60)
    print()
    print("Using plyer library for cross-platform notifications")
    print()

    # Test notifications with counter badges
    approvals = [
        ("[1] Auto Approval", "Claude Code request approved - First approval"),
        ("[2] Auto Approval", "Request approved - Total: 2"),
        ("[3] Auto Approval", "Request approved - Total: 3"),
        ("[4] Auto Approval", "Request approved - Total: 4"),
        ("[5] Auto Approval", "Request approved - Total: 5")
    ]

    for i, (title, message) in enumerate(approvals):
        timestamp = time.strftime('%H:%M:%S')
        full_title = f"{title} - {timestamp}"

        print(f"\n[Notification {i+1}/5]")
        print(f"  Title: {full_title}")
        print(f"  Message: {message}")

        success = show_plyer_notification(full_title, message, timeout=10)

        if success:
            print(f"  [SUCCESS] Notification displayed!")
        else:
            print(f"  [FAIL] Could not show notification")

        if i < len(approvals) - 1:
            print("  Waiting 2 seconds...")
            time.sleep(2)

    print("\n" + "=" * 60)
    print("Test Complete!")
    print()
    print("You should see 5 notifications:")
    print("  - Each with a counter [1] to [5] in the title")
    print("  - Timestamps for each notification")
    print("  - Approval messages")
    print()
    print("The notifications should appear in the Windows notification area")
    print("(bottom right corner of your screen)")
    print()
    print("If notifications STILL don't appear, please check:")
    print()
    print("  1. Windows Settings > System > Notifications & actions")
    print("  2. Make sure 'Get notifications from apps' is ON")
    print("  3. Scroll down and find Python.exe in the app list")
    print("  4. Make sure Python.exe is allowed to send notifications")
    print()
    print("You can also try:")
    print("  - Running the script as Administrator")
    print("  - Checking if Focus Assist is turned off")
    print("=" * 60)

if __name__ == "__main__":
    main()