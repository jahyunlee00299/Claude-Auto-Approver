#!/usr/bin/env python3
"""
Test Windows notification with actual send_approval function
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
print("Testing Windows Notification with send_approval")
print("="*70)

# First, start a Question dialog in background if not already running
print("\nMaking sure Question dialog is open...")
import subprocess
import threading

def keep_dialog_open():
    subprocess.run([sys.executable, "test_approval_dialog.py"])

# Start dialog in background thread
dialog_thread = threading.Thread(target=keep_dialog_open, daemon=True)
dialog_thread.start()

time.sleep(2)  # Wait for dialog to open

print("\nSearching for Question window...")
window = find_question_window()

if not window:
    print("ERROR: No Question window found!")
    print("Please make sure the dialog is open and try again.")
    sys.exit(1)

print(f"Found window: {window['title']}")
hwnd = window['hwnd']

print("\nCreating OCR Auto Approver instance...")
approver = OCRAutoApprover()

print("\nCalling send_approval...")
print("This should:")
print("  1. Show Windows notification")
print("  2. Activate the window")
print("  3. Send '2' key")
print("\nExecuting now...\n")

try:
    approver.send_approval(hwnd, window['title'])

    print("\n" + "="*70)
    print("send_approval completed!")
    print("="*70)
    print("\nDid you see the Windows notification appear?")
    print("Waiting 5 seconds for you to check...")
    time.sleep(5)

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
