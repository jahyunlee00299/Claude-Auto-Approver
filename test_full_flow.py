#!/usr/bin/env python3
"""
Test full flow: detect window, activate it, send '2', show notification
"""
import sys
sys.path.insert(0, '.')

from ocr_auto_approver import OCRAutoApprover
import win32gui
import time

def find_question_window():
    """Find Question window"""
    result = []

    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and 'question' in title.lower():
                windows.append({'hwnd': hwnd, 'title': title})
        return True

    win32gui.EnumWindows(callback, result)
    return result[0] if result else None

print("="*70)
print("Full Flow Test: Detect → Activate → Send '2' → Show Notification")
print("="*70)

print("\nStep 1: Please open the Question dialog")
print("Run: python test_approval_dialog.py")
print("\nWaiting 5 seconds for you to open the dialog...")
time.sleep(5)

print("\nStep 2: Searching for Question window...")
window = find_question_window()

if not window:
    print("✗ ERROR: No Question window found!")
    print("Please make sure the dialog is open and try again.")
    sys.exit(1)

print(f"✓ Found window: {window['title']}")
hwnd = window['hwnd']

print("\nStep 3: Creating OCR Auto Approver instance...")
approver = OCRAutoApprover()

print("\nStep 4: Calling send_approval (this should):")
print("  - Activate the window")
print("  - Send '2' key")
print("  - Show notification with cute character")
print("\nExecuting now...")

try:
    approver.send_approval(hwnd, window['title'])

    print("\n" + "="*70)
    print("✓ send_approval completed!")
    print("="*70)
    print("\nDid you see:")
    print("  1. The Question window get focus?")
    print("  2. The '2' key being pressed?")
    print("  3. A notification appear?")
    print("\nWaiting 5 seconds for notification to be visible...")
    time.sleep(5)

except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
