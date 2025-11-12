#!/usr/bin/env python3
"""
Test notification when other window is active
"""
import sys
sys.path.insert(0, '.')

from ocr_auto_approver import OCRAutoApprover
import time

print("="*70)
print("Notification Test - Other Window Active")
print("="*70)
print()
print("This test will:")
print("  1. Wait 5 seconds for you to switch to another window")
print("  2. Send a test notification")
print("  3. You should see the notification even in the other window")
print()
print("Instructions:")
print("  - After starting, immediately switch to your closed-loop PyCharm")
print("  - Wait for the notification to appear")
print("  - The notification should be visible even though you're in another window")
print()
print("Starting in 3 seconds...")
time.sleep(3)

print("\n" + "="*70)
print("Switch to your closed-loop PyCharm window NOW!")
print("Notification will appear in 5 seconds...")
print("="*70)

# Wait for user to switch windows
time.sleep(5)

# Create approver and send test notification
approver = OCRAutoApprover()

# Use a fake hwnd for testing
fake_hwnd = 0
test_title = "Test - Closed-Loop PyCharm Approval"

print("\n[TEST] Sending notification now...")
print("[TEST] You should see it even though you're in another window")

try:
    approver.send_approval(fake_hwnd, test_title)
    print("\n[TEST] Notification sent!")
    print("[TEST] Did you see it in your closed-loop PyCharm window?")

    # Wait a bit for notification to be visible
    time.sleep(5)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*70)
print("Test completed!")
print("If you didn't see the notification, there may be an issue with")
print("Windows notification settings or the notification is being hidden")
print("="*70)
