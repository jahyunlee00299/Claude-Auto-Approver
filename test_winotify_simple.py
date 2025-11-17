#!/usr/bin/env python3
"""
Simple winotify test - minimal example
"""
import time

try:
    from winotify import Notification, audio

    print("[TEST] Creating simple notification...")

    # Create very simple notification
    toast = Notification(
        app_id="Test App",
        title="Test Notification",
        msg="This is a test message. Can you see this notification?",
        duration="long"
    )

    # Add sound
    toast.set_audio(audio.SMS, loop=False)

    print("[TEST] Calling toast.show()...")
    toast.show()

    print("[TEST] Notification sent! Check your screen for the notification popup.")
    print("[TEST] Waiting 10 seconds...")
    time.sleep(10)

    print("[TEST] Test complete!")

except ImportError as e:
    print(f"[ERROR] winotify not installed: {e}")
    print("Run: pip install winotify")
except Exception as e:
    print(f"[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
