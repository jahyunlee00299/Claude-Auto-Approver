#!/usr/bin/env python3
"""
Test Windows Notification
"""
from winotify import Notification, audio
import time
import os

print("Testing Windows notification with image...")

try:
    # Get icon path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, 'approval_icon.png')

    print(f"Icon path: {icon_path}")
    print(f"Icon exists: {os.path.exists(icon_path)}")

    toast = Notification(
        app_id="Claude Auto Approver",
        title="AUTO APPROVING",
        msg="This is a test notification!\nSending '2' to window",
        duration="long",
        icon=icon_path
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()
    print("[OK] Notification sent!")
    print("Check the bottom-right corner of your screen.")
    print("You should see the cute character image!")
    time.sleep(5)
except Exception as e:
    print(f"[ERROR] Notification failed: {e}")
    import traceback
    traceback.print_exc()
