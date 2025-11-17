#!/usr/bin/env python3
"""
Test notification from background process - simulates auto-approver
"""
import time
from ocr_auto_approver import show_notification_popup

print("="*60)
print("Background Notification Test")
print("This simulates sending notification from auto-approver")
print("="*60)

# Wait a bit like auto-approver does
time.sleep(2)

detected_text = """Do you want to proceed?

1. Yes, proceed once
2. Yes, and don't ask again
3. No, and tell Claude what to do differently

Select an option (1-3):"""

# Prepare notification exactly like auto-approver does
lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
text_preview = '\n'.join(lines[:3])
if len(text_preview) > 150:
    text_preview = text_preview[:150] + '...'

notification_msg = f"Option '2' was automatically selected"
if text_preview:
    notification_msg += f"\n\nDetected text:\n{text_preview}"

print("\n[INFO] Sending notification...")
print(f"[DEBUG] Message length: {len(notification_msg)}")
print(f"[DEBUG] Text preview: {text_preview[:50]}...")

# Call exactly like auto-approver does
show_notification_popup(
    "Auto Approval Complete",
    notification_msg,
    window_info="Claude Code - MINGW64",
    duration=3
)

print("\n[SUCCESS] Notification sent!")
print("[CHECK] Did you see the notification popup?")
print("[CHECK] Check Action Center if not")
print("\nWaiting 3 seconds...")
time.sleep(3)
print("Done!")
