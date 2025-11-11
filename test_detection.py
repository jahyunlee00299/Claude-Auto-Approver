#!/usr/bin/env python3
"""
Test if OCR Auto Approver can detect Question window
"""
import win32gui
import time

def find_all_windows():
    """Find all visible windows"""
    result = []

    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
        return True

    win32gui.EnumWindows(callback, result)
    return result

print("="*70)
print("Window Detection Test")
print("="*70)
print("\nPlease make sure the Question dialog is open!")
print("Waiting 3 seconds...")
time.sleep(3)

print("\nSearching for windows...")
windows = find_all_windows()

print(f"\nFound {len(windows)} windows:")
print("-"*70)

question_found = False
for i, title in enumerate(windows, 1):
    # Check if it contains approval keywords
    title_lower = title.lower()
    is_approval = any(kw in title_lower for kw in ['question', 'approve', 'confirm', 'permission', 'allow'])

    if is_approval:
        print(f"{i}. [{title}] <- WOULD BE DETECTED")
        question_found = True
    else:
        safe_title = title.encode('ascii', 'ignore').decode('ascii')
        print(f"{i}. {safe_title[:60]}")

print("-"*70)

if question_found:
    print("\n✓ Found approval window(s)!")
    print("OCR Auto Approver should detect these.")
else:
    print("\n✗ No approval windows found!")
    print("Make sure the Question dialog is visible and not minimized.")
