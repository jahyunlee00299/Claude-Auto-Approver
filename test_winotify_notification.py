#!/usr/bin/env python3
"""
Test winotify notification for OCR Auto Approver
"""

import time

def show_notification_popup_winotify(title, message, duration=3):
    """
    Notification via winotify (more reliable than PowerShell)
    """
    try:
        # Add timestamp to make each notification unique
        timestamp = time.strftime('%H:%M:%S')
        unique_title = f"{title} [{timestamp}]"

        print(f"[INFO] Notification: {unique_title}")

        # Try winotify (more reliable)
        try:
            from winotify import Notification, audio

            # Create notification
            toast = Notification(
                app_id="Claude Auto Approver",
                title=unique_title,
                msg=message,
                duration="short"  # short, long
            )

            # Set to silent to avoid sound
            toast.set_audio(audio.Silent, loop=False)

            # Show notification
            toast.show()

            print(f"[OK] Windows notification sent successfully via winotify")
            return True

        except ImportError as e:
            print(f"[ERROR] winotify not available: {e}")
            return False
        except Exception as e:
            print(f"[ERROR] Failed to send winotify notification: {e}")
            return False

    except Exception as e:
        print(f"[WARNING] Notification error: {e}")
        return False


def test_notification():
    """Test the notification functionality"""

    print("=" * 70)
    print("Testing Winotify Notification for OCR Auto Approver")
    print("=" * 70)
    print()

    # Test 1: Simple notification
    print("Test 1: Simple notification")
    result = show_notification_popup_winotify(
        "Auto Approval",
        "Window: Test Application",
        duration=3
    )

    if result:
        print("[PASS] Test 1 passed - notification sent")
    else:
        print("[FAIL] Test 1 failed - notification not sent")

    time.sleep(2)

    # Test 2: Multiple notifications with different timestamps
    print("\nTest 2: Multiple notifications with different timestamps")
    for i in range(3):
        print(f"\nSending notification {i+1}/3...")
        result = show_notification_popup_winotify(
            f"Auto Approval #{i+1}",
            f"Test notification {i+1}",
            duration=3
        )

        if result:
            print(f"[PASS] Notification {i+1} sent")
        else:
            print(f"[FAIL] Notification {i+1} failed")

        time.sleep(1)

    print("\n" + "=" * 70)
    print("Test completed!")
    print("=" * 70)
    print("\nDid you see the Windows notifications?")
    print("You should have seen 4 notifications total:")
    print("  - 1 simple notification")
    print("  - 3 numbered notifications")
    print("\nIf notifications didn't appear:")
    print("  1. Check Windows notification settings")
    print("  2. Make sure notifications are enabled for Python")
    print("  3. Check if Focus Assist is turned off")


if __name__ == "__main__":
    test_notification()