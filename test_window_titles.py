#!/usr/bin/env python3
"""
Test script to show all window titles
"""
import win32gui

def list_all_windows():
    """List all visible windows with their titles"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)

    print("=" * 70)
    print("All visible windows:")
    print("=" * 70)
    for i, title in enumerate(windows, 1):
        try:
            safe_title = title.encode('ascii', 'ignore').decode('ascii')
            print(f"{i}. {safe_title}")
        except:
            print(f"{i}. [Window with special characters]")
    print("=" * 70)
    print(f"Total: {len(windows)} windows")

if __name__ == "__main__":
    list_all_windows()
