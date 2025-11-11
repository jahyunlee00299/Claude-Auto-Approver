#!/usr/bin/env python3
"""
Test send_approval function directly
"""
import sys
sys.path.insert(0, '.')

from ocr_auto_approver import OCRAutoApprover
import time

print("Testing send_approval function...")

approver = OCRAutoApprover()

# Create a fake hwnd (just use 0 for testing notification only)
fake_hwnd = 0
test_window_title = "Question - Test Approval Dialog"

print(f"\nCalling send_approval with window: {test_window_title}")
print("You should see a notification appear...")

try:
    approver.send_approval(fake_hwnd, test_window_title)
    print("\nsend_approval completed!")
    print("Did you see the notification?")
    time.sleep(3)
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
