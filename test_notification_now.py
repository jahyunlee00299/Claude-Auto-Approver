#!/usr/bin/env python3
"""Test notification immediately"""
import time
import os

def test_winotify():
    """Test winotify notification"""
    try:
        from winotify import Notification, audio

        print("[TEST] Creating winotify notification...")

        toast = Notification(
            app_id="Claude Auto Approver",
            title="✅ Test Notification",
            msg="This is a test notification from OCR Auto Approver.\n\nIf you see this, notifications are working!",
            duration="short"
        )

        # Add icon if exists
        icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
        if os.path.exists(icon_path):
            toast.icon = icon_path
            print(f"[OK] Icon added: {icon_path}")
        else:
            print(f"[INFO] No icon found at {icon_path}")

        # Set audio
        toast.set_audio(audio.SMS, loop=False)

        # Show notification
        print("[TEST] Showing notification...")
        toast.show()

        print("[SUCCESS] Notification sent!")
        print("[INFO] Check your Windows Action Center (bottom right corner)")
        print("[INFO] Or check if a toast notification appeared")

        # Keep script running for a moment
        time.sleep(5)

        return True

    except Exception as e:
        print(f"[ERROR] winotify failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("="*60)
    print("Windows Notification Test")
    print("="*60)
    print()

    success = test_winotify()

    if success:
        print("\n[SUCCESS] Test completed - check for notification!")
    else:
        print("\n[FAILED] Test failed - see error above")
