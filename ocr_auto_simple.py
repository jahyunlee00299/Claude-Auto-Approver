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
        log(f"Sending '1' to: {safe_title}")

        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.3)

        # Smart navigation with Alt + arrows, monitoring OCR changes
        VK_RIGHT = 0x27
        VK_LEFT = 0x25
        VK_MENU = 0x12  # Alt key
        VK_RETURN = 0x0D  # Enter key

        # Capture initial screen
        initial_img = capture_window(hwnd)
        initial_text = pytesseract.image_to_string(initial_img, lang='eng') if initial_img else ""

        # Check initial screen for target
        if "don't ask again" in initial_text.lower() or "yes, and don" in initial_text.lower():
            log(f"Found target on initial screen!")
            win32api.keybd_event(VK_RETURN, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        else:
            # Determine navigation direction
            direction_key = None
            direction_name = ""

            # Try Right first
            win32api.keybd_event(VK_MENU, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(VK_RIGHT, 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(VK_RIGHT, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.05)
            win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(0.2)

            test_img = capture_window(hwnd)
            test_text = pytesseract.image_to_string(test_img, lang='eng') if test_img else ""

            if test_text != initial_text:
                # Right works!
                direction_key = VK_RIGHT
                direction_name = "Right"
                log(f"Right navigation works, continuing...")

                # Check if we found it
                if "don't ask again" in test_text.lower() or "yes, and don" in test_text.lower():
                    log(f"Found target after 1 Right!")
                    win32api.keybd_event(VK_RETURN, 0, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                    direction_key = None
                else:
                    initial_text = test_text
            else:
                # Right didn't work, try Left
                log(f"Right didn't work, trying Left...")
                win32api.keybd_event(VK_MENU, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(VK_LEFT, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(VK_LEFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
                win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.2)

                test_img = capture_window(hwnd)
                test_text = pytesseract.image_to_string(test_img, lang='eng') if test_img else ""

                if test_text != initial_text:
                    # Left works!
                    direction_key = VK_LEFT
                    direction_name = "Left"
                    log(f"Left navigation works, continuing...")

                    # Check if we found it
                    if "don't ask again" in test_text.lower() or "yes, and don" in test_text.lower():
                        log(f"Found target after 1 Left!")
                        win32api.keybd_event(VK_RETURN, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                        direction_key = None
                    else:
                        initial_text = test_text

            # Continue in determined direction
            if direction_key:
                found = False
                presses_count = 1  # Already pressed once

                for i in range(5):  # Max 5 more tries
                    # Press Alt + direction
                    win32api.keybd_event(VK_MENU, 0, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(direction_key, 0, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(direction_key, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.2)
                    presses_count += 1

                    new_img = capture_window(hwnd)
                    new_text = pytesseract.image_to_string(new_img, lang='eng') if new_img else ""

                    # Check if we found the target
                    if "don't ask again" in new_text.lower() or "yes, and don" in new_text.lower():
                        log(f"Found target after {presses_count} {direction_name} presses!")
                        win32api.keybd_event(VK_RETURN, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                        found = True
                        break

                    # If content didn't change, reached the end
                    if new_text == initial_text:
                        log(f"Reached end in {direction_name} direction after {presses_count} presses")
                        break

                    initial_text = new_text

                # If not found, go back to start and try opposite direction
                if not found:
                    log(f"Going back to start to try opposite direction...")

                    # Go back by pressing opposite direction same number of times
                    opposite_key = VK_LEFT if direction_key == VK_RIGHT else VK_RIGHT
                    opposite_name = "Left" if direction_key == VK_RIGHT else "Right"

                    for _ in range(presses_count):
                        win32api.keybd_event(VK_MENU, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(opposite_key, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(opposite_key, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(0.1)

                    log(f"Now trying {opposite_name} direction...")

                    # Capture initial again
                    initial_img = capture_window(hwnd)
                    initial_text = pytesseract.image_to_string(initial_img, lang='eng') if initial_img else ""

                    # Try opposite direction
                    for i in range(6):
                        win32api.keybd_event(VK_MENU, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(opposite_key, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(opposite_key, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(0.2)

                        new_img = capture_window(hwnd)
                        new_text = pytesseract.image_to_string(new_img, lang='eng') if new_img else ""

                        # Check if we found the target
                        if "don't ask again" in new_text.lower() or "yes, and don" in new_text.lower():
                            log(f"Found target after {i+1} {opposite_name} presses!")
                            win32api.keybd_event(VK_RETURN, 0, 0, 0)
                            time.sleep(0.05)
                            win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                            found = True
                            break

                        # If content didn't change, reached the end
                        if new_text == initial_text:
                            log(f"Reached end in {opposite_name} direction, no more options")
                            break

                        initial_text = new_text

                    # Still not found, fallback - send '1' (Yes) as safest option
                    if not found:
                        log(f"Exhausted both directions, sending '1' as fallback")
                        win32api.keybd_event(ord('1'), 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

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
