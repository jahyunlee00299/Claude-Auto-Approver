#!/usr/bin/env python3
"""Simple OCR Auto Approver with file logging"""
import time
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

log_file = open('ocr_auto_approver.log', 'w', encoding='utf-8')

def log(msg):
    timestamp = time.strftime('%H:%M:%S')
    line = f"[{timestamp}] {msg}\n"
    log_file.write(line)
    log_file.flush()
    print(line.strip())

log("Starting OCR Auto Approver")

patterns = [
    'Do you want to proceed?',
    '1. Yes',
    '1. Approve',
    '1) Yes',
    '2. Yes, and don',  # "Yes, and don't ask again"
    '3. No, and tell',   # "No, and tell Claude"
    'want to proceed',
    'Select an option',
    # Korean patterns
    '조치', '선택'
]
exclude = ['chrome', 'firefox']  # Only exclude browsers
last_approval = {}
approval_count = 0

def find_windows():
    windows = []
    def callback(hwnd, results):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title:
                if not any(e in title.lower() for e in exclude):
                    results.append((hwnd, title))
        return True

    win32gui.EnumWindows(callback, windows)
    return windows

def capture_window(hwnd):
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

        win32gui.DeleteObject(saveBitMap.GetHandle())
        saveDC.DeleteDC()
        mfcDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, hwndDC)

        return img
    except:
        return None

def check_text(text):
    for pattern in patterns:
        if pattern.lower() in text.lower():
            return True
    return False

def send_approval(hwnd, title):
    global approval_count
    try:
        safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
        log(f"Sending '2' to: {safe_title}")

        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        win32api.keybd_event(ord('2'), 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)

        approval_count += 1
        last_approval[hwnd] = time.time()
        log(f"Approved! Total: {approval_count}")
        return True
    except Exception as e:
        log(f"Error: {e}")
        return False

log("Monitoring started. Check every 3 seconds.")
log(f"Looking for patterns: {patterns}")

try:
    while True:
        windows = find_windows()
        log(f"Scanning {len(windows)} windows...")

        for hwnd, title in windows[:10]:  # Scan up to 10 windows
            # Check cooldown
            if hwnd in last_approval:
                if time.time() - last_approval[hwnd] < 10:
                    safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
                    log(f"  Skipping (cooldown): {safe_title}")
                    continue

            safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
            log(f"  Checking: {safe_title}")

            img = capture_window(hwnd)
            if not img:
                log(f"    Failed to capture")
                continue

            text = pytesseract.image_to_string(img, lang='eng')
            log(f"    OCR: {len(text)} chars")

            if check_text(text):
                log(f"    FOUND approval request!")
                send_approval(hwnd, title)

        time.sleep(3)

except KeyboardInterrupt:
    log("Stopped by user")
except Exception as e:
    log(f"Error: {e}")
finally:
    log(f"Total approvals: {approval_count}")
    log_file.close()
