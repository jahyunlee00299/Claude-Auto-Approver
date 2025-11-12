#!/usr/bin/env python3
"""
Quick notification test with detected text
"""
import time
from ocr_auto_approver import show_notification_popup

print("="*60)
print("Quick Notification Test")
print("="*60)

# Simulate detected text from a 3-option dialog
detected_text_3options = """Would you like to proceed with this edit?

1. Yes, proceed once
2. Yes, and don't ask again
3. No, and tell Claude what to do differently

Select an option (1-3):"""

# Prepare text preview
lines = [line.strip() for line in detected_text_3options.split('\n') if line.strip()]
text_preview = '\n'.join(lines[:3])
if len(text_preview) > 150:
    text_preview = text_preview[:150] + '...'

notification_msg = "Option '2' was automatically selected\n\nDetected text:\n" + text_preview

print("\nTest 1: Notification with 3-option dialog text")
print(f"Message length: {len(notification_msg)}")
print(f"Text preview:\n{text_preview}\n")

show_notification_popup(
    "Auto Approval Complete",
    notification_msg,
    window_info="Claude Code - Test Window",
    duration=5
)

print("[OK] Notification sent!")
print("\n[CHECK] Windows Action Center (bottom-right corner)")
print("[CHECK] You should see:")
print("  - Title: 'Auto Approval Complete'")
print("  - Option selected: '2'")
print("  - First 3 lines of detected text")
print("  - Cute approval icon")
print("\nWaiting 5 seconds...")

time.sleep(5)

# Test 2: 2-option dialog
print("\n" + "="*60)
detected_text_2options = """Do you want to allow this action?

1. Yes, allow once
2. No, cancel

Select an option (1-2):"""

lines = [line.strip() for line in detected_text_2options.split('\n') if line.strip()]
text_preview = '\n'.join(lines[:3])

notification_msg = "Option '1' was automatically selected\n\nDetected text:\n" + text_preview

print("\nTest 2: Notification with 2-option dialog text")
print(f"Text preview:\n{text_preview}\n")

show_notification_popup(
    "Auto Approval Complete",
    notification_msg,
    window_info="Claude Code - Another Test",
    duration=5
)

print("[OK] Second notification sent!")
print("\n=== All tests complete! ===")
