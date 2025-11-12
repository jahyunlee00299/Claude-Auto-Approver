#!/usr/bin/env python3
"""
Windows 10 Toast Notification Test
"""
import time
from win10toast import ToastNotifier
import winsound

def show_toast_notification(title, message, duration=5):
    """
    Show Windows 10 toast notification using win10toast
    """
    try:
        # Create ToastNotifier instance
        toaster = ToastNotifier()

        # Play sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # Show toast notification
        success = toaster.show_toast(
            title,
            message,
            icon_path=None,  # Use default icon
            duration=duration,
            threaded=True  # Non-blocking
        )

        return success
    except Exception as e:
        print(f"[ERROR] Failed to show toast: {e}")
        return False

def main():
    print("=" * 60)
    print("Windows 10 Toast Notification Test")
    print("=" * 60)
    print()
    print("Using win10toast library to show notifications")
    print()

    # Test notifications
    notifications = [
        ("[1] Auto Approval", "Claude Code request approved\nFirst approval today"),
        ("[2] Auto Approval", "Another request approved\nTotal: 2 approvals"),
        ("[3] Auto Approval", "Third request approved\nAll approvals successful"),
    ]

    for i, (title, message) in enumerate(notifications):
        timestamp = time.strftime('%H:%M:%S')
        full_title = f"{title} - {timestamp}"

        print(f"\n[Test {i+1}/3]")
        print(f"  Title: {full_title}")
        print(f"  Message: {message}")

        success = show_toast_notification(full_title, message)

        if success:
            print(f"  [SUCCESS] Toast notification sent!")
        else:
            print(f"  [FAIL] Could not send notification")

        if i < len(notifications) - 1:
            print("  Waiting 3 seconds...")
            time.sleep(3)

    print("\n" + "=" * 60)
    print("Test Complete!")
    print()
    print("Check Windows notification area (bottom right corner)")
    print("You should see 3 toast notifications with counters [1], [2], [3]")
    print()
    print("If notifications still don't appear:")
    print("  1. Open Windows Settings")
    print("  2. Go to System > Notifications & actions")
    print("  3. Make sure notifications are turned ON")
    print("  4. Check that Python/Python.exe is allowed to send notifications")
    print("=" * 60)

if __name__ == "__main__":
    main()