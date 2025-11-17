import win32gui
import win32con

def list_all_windows():
    """List all visible windows with their titles"""
    def callback(hwnd, windows):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                try:
                    class_name = win32gui.GetClassName(hwnd)
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    width = right - left
                    height = bottom - top

                    # Print in safe ASCII
                    safe_title = title.encode('ascii', 'ignore').decode('ascii')
                    print(f"Title: {safe_title[:60]}")
                    print(f"  Class: {class_name}")
                    print(f"  Size: {width}x{height}")
                    print(f"  HWND: {hwnd}")
                    print()
                except:
                    pass
        return True

    print("="*70)
    print("All Visible Windows")
    print("="*70)
    win32gui.EnumWindows(callback, None)

if __name__ == "__main__":
    list_all_windows()
