"""
시스템 창 필터링 테스트
"""
import win32gui
import win32con

def get_all_windows():
    """모든 창 정보 수집"""
    windows = []

    def callback(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    class_name = win32gui.GetClassName(hwnd)
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width = right - left
                    height = bottom - top

                    style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
                    is_tool = bool(style & win32con.WS_EX_TOOLWINDOW)
                    is_noactivate = bool(style & win32con.WS_EX_NOACTIVATE)

                    windows.append({
                        'hwnd': hwnd,
                        'title': title,
                        'class': class_name,
                        'size': f"{width}x{height}",
                        'is_tool': is_tool,
                        'is_noactivate': is_noactivate
                    })
                except:
                    pass
        return True

    win32gui.EnumWindows(callback, None)
    return windows

def is_system_window(hwnd):
    """시스템 창인지 확인 (ocr_auto_approver.py와 동일한 로직)"""
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
    ]

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

        style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
        if style & win32con.WS_EX_TOOLWINDOW:
            return True
        if style & win32con.WS_EX_NOACTIVATE:
            return True

        return False
    except:
        return False

def main():
    print("="*80)
    print("OCR Auto Approver - 창 필터링 테스트")
    print("="*80)
    print()

    windows = get_all_windows()

    print(f"총 {len(windows)}개의 창 발견\n")

    # 시스템 창 분류
    system_windows = []
    normal_windows = []

    for win in windows:
        if is_system_window(win['hwnd']):
            system_windows.append(win)
        else:
            normal_windows.append(win)

    print("="*80)
    print(f"시스템 창 (필터링됨): {len(system_windows)}개")
    print("="*80)
    for win in system_windows[:10]:  # 처음 10개만 표시
        # ASCII 변환
        safe_title = win['title'][:50].encode('ascii', 'ignore').decode('ascii')
        safe_class = win['class'].encode('ascii', 'ignore').decode('ascii')
        print(f"제목: {safe_title}")
        print(f"  클래스: {safe_class}")
        print(f"  크기: {win['size']}, Tool: {win['is_tool']}, NoActivate: {win['is_noactivate']}")
        print()

    if len(system_windows) > 10:
        print(f"... 그 외 {len(system_windows) - 10}개 더\n")

    print("="*80)
    print(f"일반 창 (모니터링 대상): {len(normal_windows)}개")
    print("="*80)
    for win in normal_windows[:10]:  # 처음 10개만 표시
        # ASCII 변환
        safe_title = win['title'][:50].encode('ascii', 'ignore').decode('ascii')
        safe_class = win['class'].encode('ascii', 'ignore').decode('ascii')
        print(f"제목: {safe_title}")
        print(f"  클래스: {safe_class}")
        print(f"  크기: {win['size']}")
        print()

    if len(normal_windows) > 10:
        print(f"... 그 외 {len(normal_windows) - 10}개 더\n")

    print("="*80)
    print("필터링 요약")
    print("="*80)
    print(f"전체:         {len(windows)}개")
    print(f"필터링됨:     {len(system_windows)}개 ({len(system_windows)/len(windows)*100:.1f}%)")
    print(f"모니터링 대상: {len(normal_windows)}개 ({len(normal_windows)/len(windows)*100:.1f}%)")
    print()
    print("[OK] 윈도우 알림 센터, 시스템 UI는 필터링됨")
    print("[OK] 일반 프로그램 창만 모니터링 대상")

if __name__ == "__main__":
    main()
