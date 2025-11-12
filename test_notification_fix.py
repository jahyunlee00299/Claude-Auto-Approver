#!/usr/bin/env python3
"""
Test the fixed notification in OCR Auto Approver
"""
import sys
sys.path.insert(0, '.')

from ocr_auto_approver import OCRAutoApprover
import time

print("="*70)
print("Testing Fixed Notification System")
print("="*70)

approver = OCRAutoApprover()

# Create a fake window info for testing
fake_hwnd = 12345
fake_title = "Test Window - PowerShell"

print("\nCalling send_approval with fake window...")
print("You should see a Windows notification appear!\n")

# Call the send_approval method directly
# This will attempt to send '2' to the fake window (which will fail)
# but the notification should still appear
try:
    approver.send_approval(fake_hwnd, fake_title)
    print("\n" + "="*70)
    print("Notification test completed!")
    print("="*70)
    print("\nDid you see the Windows notification?")
    print("It should have:")
    print("  - Title: 'Auto Approval [HH:MM:SS]'")
    print("  - Message: 'Window: PowerShell'")
    print("  - Icon: Cute character image")
    print("  - Sound: Default notification sound")
except Exception as e:
    print(f"\nError during test: {e}")
    import traceback
    traceback.print_exc()

print("\nWaiting 3 seconds to let you see the notification...")
time.sleep(3)
print("Test finished!")
