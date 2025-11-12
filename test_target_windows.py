#!/usr/bin/env python3
"""
타겟 윈도우 감지 테스트 - ocr_auto_approver의 로직을 테스트
"""
import sys
import io
import win32gui
import win32con

# UTF-8 encoding for console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Copy the filtering logic from ocr_auto_approver
exclude_keywords = [
    'claude auto approver',
    'auto approval',
    'chrome',
    'google chrome',
    'nvidia geforce',
    'program manager',
    'microsoft text input',
    'settings',
    '설정',
]

system_classes = [
    'Windows.UI.Core.CoreWindow',
    'Shell_TrayWnd',
    'NotifyIconOverflowWindow',
    'Windows.UI.Input.InputSite.WindowClass',
    'ApplicationFrameWindow',
    'Windows.Internal.Shell.TabProxyWindow',
    'ImmersiveLauncher',
    'MultitaskingViewFrame',
    'ForegroundStaging',
    'Dwm',
]

def is_system_window(hwnd):
    """Check if window is a system window"""
    try:
        class_name = win32gui.GetClassName(hwnd)

        if class_name in system_classes:
            return True

        if 'notification' in class_name.lower():
            return True
        if 'toast' in class_name.lower():
            return True
        if 'windows.ui' in class_name.lower():
            return True
        if 'xaml' in class_name.lower():
            return True
        if 'dwm' in class_name.lower():
            return True

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if style & win32con.WS_EX_TOOLWINDOW:
            return True
        if style & win32con.WS_EX_NOACTIVATE:
            return True

        try:
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            if left == -32000 and top == -32000:
                return True
        except:
            pass

        return False

    except Exception:
        return False

def find_target_windows():
    """Find all visible windows with filtering"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                # Exclude system windows first
                if is_system_window(hwnd):
                    return True

                # Exclude keywords
                title_lower = title.lower()
                is_excluded = any(exc in title_lower for exc in exclude_keywords)

                if not is_excluded:
                    try:
                        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                        width = right - left
                        height = bottom - top

                        if width >= 100 and height >= 20:
                            try:
                                class_name = win32gui.GetClassName(hwnd)
                            except:
                                class_name = "Unknown"

                            windows.append({
                                'hwnd': hwnd,
                                'title': title,
                                'class': class_name,
                                'pos': (left, top, right, bottom),
                                'size': (width, height)
                            })
                    except:
                        pass
        return True

    windows = []
    try:
        win32gui.EnumWindows(callback, windows)
    except:
        pass
    return windows

def main():
    print("="*80)
    print("타겟 윈도우 감지 테스트 (OCRAutoApprover 로직)")
    print("="*80)
    print()

    # Find all windows
    all_windows = []
    def callback_all(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                windows.append(title)
        return True

    win32gui.EnumWindows(callback_all, all_windows)
    print(f"전체 윈도우 수: {len(all_windows)}")

    # Find target windows
    target_windows = find_target_windows()
    print(f"타겟 윈도우 수: {len(target_windows)} (필터링 후)")
    print()

    if target_windows:
        print("타겟 윈도우 목록:")
        print("-"*80)
        for i, win in enumerate(target_windows, 1):
            width, height = win['size']
            print(f"{i:2}. [{win['hwnd']:8}] {width:4}x{height:4}")
            print(f"    제목: {win['title']}")
            print(f"    클래스: {win['class']}")
            print(f"    위치: {win['pos']}")
            print()
    else:
        print("⚠️  타겟 윈도우를 찾지 못했습니다!")
        print()
        print("가능한 원인:")
        print("  - 모든 윈도우가 exclude_keywords에 포함됨")
        print("  - 모든 윈도우가 시스템 윈도우로 필터링됨")
        print("  - 윈도우 크기가 100x20보다 작음")

    print("="*80)

    # Show which windows were filtered out and why
    print("\n필터링된 윈도우 분석:")
    print("-"*80)

    filtered_count = {
        'system_window': 0,
        'excluded_keyword': 0,
        'too_small': 0,
        'no_title': 0
    }

    def analyze_callback(hwnd, data):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)

            if not title:
                filtered_count['no_title'] += 1
                return True

            if is_system_window(hwnd):
                filtered_count['system_window'] += 1
                print(f"  [시스템] {title[:50]}")
                return True

            title_lower = title.lower()
            is_excluded = any(exc in title_lower for exc in exclude_keywords)
            if is_excluded:
                filtered_count['excluded_keyword'] += 1
                matching_keywords = [exc for exc in exclude_keywords if exc in title_lower]
                print(f"  [제외키워드: {matching_keywords[0]}] {title[:40]}")
                return True

            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                width = right - left
                height = bottom - top

                if width < 100 or height < 20:
                    filtered_count['too_small'] += 1
                    return True
            except:
                pass

        return True

    win32gui.EnumWindows(analyze_callback, None)

    print(f"\n필터링 통계:")
    print(f"  - 제목 없음: {filtered_count['no_title']}개")
    print(f"  - 시스템 윈도우: {filtered_count['system_window']}개")
    print(f"  - 제외 키워드: {filtered_count['excluded_keyword']}개")
    print(f"  - 너무 작음 (<100x20): {filtered_count['too_small']}개")
    print("="*80)

if __name__ == "__main__":
    main()
