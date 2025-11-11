#!/usr/bin/env python3
import win32gui
import win32ui
import win32con
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

patterns = ['Do you want to proceed?', '1. Yes', '2. Yes', '3. No', 'proceed?']
found_windows = []

def capture_and_check(hwnd, title):
    try:
        left, top, right, bottom = win32gui.GetWindowRect(hwnd)
        width = right - left
        height = bottom - top

        if width < 100 or height < 100:
            return None

        hwndDC = win32gui.GetWindowDC(hwnd)
        mfcDC = win32ui.CreateDCFromHandle(hwndDC)
        saveDC = mfcDC.CreateCompatibleDC()

        saveBitMap = win32ui.CreateBitmap()
        saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
        saveDC.SelectObject(saveBitMap)
        saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

        bmpinfo = saveBitMap.GetInfo()
        bmpstr = saveBitMap.GetBitmapBits(True)
        img = Image.frombuffer('RGB', (bmpinfo['bmWidth'], bmpinfo['bmHeight']), bmpstr, 'raw', 'BGRX', 0, 1)

        # Bottom 30%
        bottom_region = img.crop((0, int(height * 0.7), width, height))

        text = pytesseract.image_to_string(bottom_region, lang='eng')

        # Cleanup
        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        # Check patterns
        for pattern in patterns:
            if pattern.lower() in text.lower():
                return text

        return None
    except:
        return None

def enum_callback(hwnd, results):
    if win32gui.IsWindowVisible(hwnd):
        title = win32gui.GetWindowText(hwnd)
        if title:
            exclude = ['.md', '.txt', '.py', 'chrome', 'firefox']
            if not any(e in title.lower() for e in exclude):
                results.append((hwnd, title))
    return True

windows = []
win32gui.EnumWindows(enum_callback, windows)

print(f"Scanning {len(windows)} windows...")

for i, (hwnd, title) in enumerate(windows[:10]):  # Scan first 10
    try:
        safe_title = title.encode('ascii', 'ignore').decode('ascii')
        print(f"{i+1}. Checking: {safe_title[:50]}...")
    except:
        print(f"{i+1}. Checking window...")

    text = capture_and_check(hwnd, title)
    if text:
        print(f"   FOUND APPROVAL REQUEST!")
        try:
            safe_title = title.encode('ascii', 'ignore').decode('ascii')
            print(f"   Window: {safe_title}")
        except:
            print(f"   Window: (special chars)")

        with open(f'approval_found_{i}.txt', 'w', encoding='utf-8') as f:
            f.write(f"Window: {title}\n\n")
            f.write(text)

        print(f"   Saved to approval_found_{i}.txt")
        found_windows.append(title)

print(f"\nDone! Found {len(found_windows)} windows with approval requests")
for w in found_windows:
    try:
        print(f"  - {w}")
    except:
        print(f"  - (special chars)")
