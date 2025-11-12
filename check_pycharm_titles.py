#!/usr/bin/env python3
"""Check PyCharm window titles"""
import win32gui

def callback(hwnd, windows):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title and 'pycharm' in title.lower():
            print(f"PyCharm Window: {title}")
            windows.append(title)
    return True

windows = []
win32gui.EnumWindows(callback, windows)

if not windows:
    print("No PyCharm windows found")
