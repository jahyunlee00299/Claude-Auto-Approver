import win32gui

def list_all_windows():
    windows = []

    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                class_name = win32gui.GetClassName(hwnd)
                results.append({'hwnd': hwnd, 'title': title, 'class': class_name})
        return True

    win32gui.EnumWindows(callback, windows)

    # Sort by title
    windows.sort(key=lambda x: x['title'])

    print(f"Total visible windows: {len(windows)}\n")
    print("=" * 100)

    for i, win in enumerate(windows, 1):
        try:
            safe_title = win['title'].encode('ascii', 'ignore').decode('ascii')
            print(f"{i:3}. [{win['class'][:30]}] {safe_title}")
        except:
            print(f"{i:3}. [{win['class'][:30]}] (special chars)")

    print("=" * 100)

if __name__ == "__main__":
    list_all_windows()
