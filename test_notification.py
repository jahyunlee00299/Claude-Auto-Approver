#!/usr/bin/env python3
"""
Test notification with detected text preview
"""
import time
from ocr_auto_approver import show_notification_popup

# Test 1: Simple notification
print("Test 1: Simple notification without detected text")
show_notification_popup(
    "Auto Approval Complete",
    "Option '2' was automatically selected",
    window_info="MINGW64:/c/Users/Jahyun/Test",
    duration=3
)
print("Notification 1 sent!")
time.sleep(4)

# Test 2: Notification with detected text
print("\nTest 2: Notification with detected text preview")
detected_text = """Would you like to proceed with this action?

1. Yes, proceed once
2. Yes, and don't ask again for this session
3. No, cancel this action

Select an option (1-3):"""

# Prepare detected text preview (first 3 lines, max 150 chars)
text_preview = ''
if detected_text:
    lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
    text_preview = '\n'.join(lines[:3])
    if len(text_preview) > 150:
        text_preview = text_preview[:150] + '...'

notification_msg = "Option '2' was automatically selected"
if text_preview:
    notification_msg += f"\n\nDetected text:\n{text_preview}"

show_notification_popup(
    "Auto Approval Complete",
    notification_msg,
    window_info="Claude Code - MINGW64",
    duration=5
)
print("Notification 2 sent with detected text!")
time.sleep(6)

# Test 3: Notification with long detected text (should be truncated)
print("\nTest 3: Notification with long detected text (should be truncated)")
long_text = """Claude Code is requesting permission to edit files.

1. Yes, allow this edit
2. Yes, and allow all edits without asking again
3. No, and tell Claude what to do differently

This is a very long approval dialog that contains a lot of text.
It should be truncated in the notification to avoid overwhelming the user.
We only show the first few lines to give context about what was detected."""

lines = [line.strip() for line in long_text.split('\n') if line.strip()]
text_preview = '\n'.join(lines[:3])
if len(text_preview) > 150:
    text_preview = text_preview[:150] + '...'

notification_msg = "Option '1' was automatically selected"
if text_preview:
    notification_msg += f"\n\nDetected text:\n{text_preview}"

show_notification_popup(
    "Auto Approval Complete",
    notification_msg,
    window_info="Python - test_notification.py",
    duration=5
)
print("Notification 3 sent with truncated text!")
print("\n=== All tests completed! ===")
