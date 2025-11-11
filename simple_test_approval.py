#!/usr/bin/env python3
"""
Simple test - just print "APPROVAL" when '2' is pressed
"""
import win32gui
import win32api
import win32con
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

print("Waiting for Question window...")
time.sleep(3)

window = find_question_window()
if not window:
    print("No Question window found!")
else:
    print(f"Found: {window['title']}")
    print("Activating window and sending '2'...")

    # Activate window
    try:
        win32gui.SetForegroundWindow(window['hwnd'])
    except:
        pass

    time.sleep(0.5)

    # Print APPROVAL message
    print("\n" + "="*50)
    print("🔔 APPROVAL DETECTED 🔔")
    print(f"Window: {window['title']}")
    print(f"Action: Sending '2' key")
    print("="*50 + "\n")

    # Send '2' key
    win32api.keybd_event(ord('2'), 0, 0, 0)
    time.sleep(0.05)
    win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)

    print("✅ Done!")
