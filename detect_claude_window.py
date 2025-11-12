#!/usr/bin/env python3
"""
Detect Claude Code approval window title
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
print("Claude Code Approval Window Detector")
print("="*70)
print()
print("Instructions:")
print("  1. Go to your closed-loop PyCharm")
print("  2. Trigger a Claude Code action that requires approval")
print("  3. This script will show all window titles every 2 seconds")
print("  4. Look for the approval dialog window title")
print()
print("Starting in 3 seconds...")
time.sleep(3)

print("\n" + "="*70)
print("Monitoring windows... (Press Ctrl+C to stop)")
print("="*70)

try:
    count = 0
    while True:
        count += 1
        print(f"\n[Scan #{count}] {time.strftime('%H:%M:%S')}")
        print("-"*70)

        windows = find_all_windows()

        # Look for potential approval windows
        for title in windows:
            title_lower = title.lower()

            # Check for keywords that might indicate approval dialog
            is_approval = any(kw in title_lower for kw in [
                'question', 'approve', 'confirm', 'permission', 'allow',
                'claude', 'approval', 'dialog', 'bash', 'git', 'command'
            ])

            if is_approval:
                print(f">>> {title} <<<")
            else:
                safe_title = title.encode('ascii', 'ignore').decode('ascii')
                if safe_title.strip():
                    print(f"    {safe_title[:60]}")

        time.sleep(2)

except KeyboardInterrupt:
    print("\n\n[INFO] Stopped by user")
    print("="*70)
