#!/usr/bin/env python3
"""
현재 열린 창 목록 확인
"""
import sys
import io
import win32gui

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def list_windows():
    """모든 창 목록 출력"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)

    print("현재 열린 창 목록:")
    print("=" * 70)
    for i, title in enumerate(windows, 1):
        print(f"{i}. {title}")
    print("=" * 70)
    print(f"총 {len(windows)}개 창")

if __name__ == "__main__":
    list_windows()
