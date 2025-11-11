#!/usr/bin/env python3
"""
모든 창 목록 출력 - 디버그용
"""
import win32gui
import sys
import io

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def list_all_windows():
    """모든 창 목록 출력"""
    windows = []

    def callback(hwnd, extra):
        try:
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    windows.append({
                        'hwnd': hwnd,
                        'title': title
                    })
        except:
            pass
        return True

    win32gui.EnumWindows(callback, None)

    print(f"\n{'='*80}")
    print(f"총 {len(windows)}개의 보이는 창 발견:")
    print(f"{'='*80}\n")

    for i, win in enumerate(windows, 1):
        title_lower = win['title'].lower()

        # 관심 있는 키워드 표시
        keywords = ['pycharm', 'catapro', 'bash', 'mingw', 'git', 'claude',
                   'terminal', 'cmd', 'powershell', 'python']

        marker = ""
        for keyword in keywords:
            if keyword in title_lower:
                marker = f" ⭐ [{keyword.upper()}]"
                break

        print(f"{i:3d}. {win['title']}{marker}")
        print(f"     hwnd: {win['hwnd']}")
        print()

if __name__ == "__main__":
    list_all_windows()
