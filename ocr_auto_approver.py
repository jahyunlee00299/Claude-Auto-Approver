#!/usr/bin/env python3
"""
OCR Auto Approver - OCR로 승인 요청 감지 + 자동 "1" 입력
"""
import sys
import time
import threading
import win32gui
import win32ui
import win32con
import win32api
import win32console
import winsound
from PIL import Image
import pytesseract
import io
from winotify import Notification, audio

# No UTF-8 configuration - use ASCII only for output to avoid encoding issues

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRAutoApprover:
    """OCR-based approval detection and auto-input"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # Approval patterns
        self.approval_patterns = [
            'Do you want to proceed?',
            '1. Yes',
            '2. Yes, and don\'t ask again',
            '3. No, and tell Claude',
            '1. Approve',
            '1. OK',
            '1) Yes',
            '1: Yes',
            'option (1-',
            'Select (1)',
        ]

        # Exclude keywords
        self.exclude_keywords = ['readme', '.md', '.txt', '.py', 'editor']

        # Duplicate prevention - track per window
        self.last_approval_per_window = {}
        self.min_approval_interval = 10  # Auto-approve once per 10 seconds per window

        # Current window
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

        print("[OK] OCR Auto Approver initialized")

    def find_target_windows(self):
        """Find all visible windows (including current)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Include current window
                    # Exclude keywords
                    title_lower = title.lower()
                    is_excluded = any(exc in title_lower for exc in self.exclude_keywords)

                    if not is_excluded:
                        windows.append({'hwnd': hwnd, 'title': title})
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def capture_window(self, hwnd):
        """Capture window screenshot"""
        try:
            # Get window size
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # Minimum size check
            if width < 100 or height < 100:
                return None

            # Device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # Copy screen
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            # Convert to PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1
            )

            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return img

        except Exception:
            return None

    def extract_text_from_image(self, img):
        """Extract text from image (OCR)"""
        try:
            # Try full image first
            text = pytesseract.image_to_string(img, lang='eng')

            # If too little text, try bottom half
            if len(text) < 50:
                width, height = img.size
                bottom_region = img.crop((0, int(height * 0.5), width, height))
                text = pytesseract.image_to_string(bottom_region, lang='eng')

            return text

        except Exception:
            return ""

    def check_approval_pattern(self, text):
        """Check if text contains approval pattern"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.approval_patterns:
            if pattern.lower() in text_lower:
                return True

        return False

    def should_approve(self, hwnd):
        """Check if should auto-approve (prevent duplicates)"""
        current_time = time.time()

        # Prevent too frequent approvals on same window
        if hwnd in self.last_approval_per_window:
            last_time = self.last_approval_per_window[hwnd]
            if current_time - last_time < self.min_approval_interval:
                return False

        return True

    def send_approval(self, hwnd, window_title):
        """Send '1' input to window (no Enter)"""
        try:
            # Show notification
            try:
                toast = Notification(
                    app_id="Claude Auto Approver",
                    title="Auto Approval",
                    msg=f"Sending '2' to window:\n{window_title[:50]}",
                    duration="short"
                )
                toast.set_audio(audio.Default, loop=False)
                toast.show()
            except:
                pass

            # Beep
            winsound.MessageBeep(winsound.MB_ICONASTERISK)

            # Activate window
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.3)  # Window activation delay

            # Smart navigation with Alt + arrows, monitoring OCR changes
            VK_RIGHT = 0x27
            VK_LEFT = 0x25
            VK_MENU = 0x12  # Alt key
            VK_RETURN = 0x0D  # Enter key

            # Capture initial screen
            time.sleep(0.3)  # Wait for screen to stabilize
            initial_img = self.capture_window(hwnd)
            initial_text = self.extract_text_from_image(initial_img) if initial_img else ""

            # Check initial screen for target
            if "don't ask again" in initial_text.lower() or "yes, and don" in initial_text.lower():
                print(f"[INFO] Found target on initial screen!")
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
                time.sleep(0.3)  # Wait for tab switch and screen update

                test_img = self.capture_window(hwnd)
                test_text = self.extract_text_from_image(test_img) if test_img else ""

                if test_text != initial_text:
                    # Right works!
                    direction_key = VK_RIGHT
                    direction_name = "Right"
                    print(f"[INFO] Right navigation works, continuing...")

                    # Check if we found it
                    if "don't ask again" in test_text.lower() or "yes, and don" in test_text.lower():
                        print(f"[INFO] Found target after 1 Right!")
                        win32api.keybd_event(VK_RETURN, 0, 0, 0)
                        time.sleep(0.05)
                        win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                        direction_key = None
                    else:
                        initial_text = test_text
                else:
                    # Right didn't work, try Left
                    print(f"[INFO] Right didn't work, trying Left...")
                    win32api.keybd_event(VK_MENU, 0, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(VK_LEFT, 0, 0, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(VK_LEFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.05)
                    win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                    time.sleep(0.3)  # Wait for tab switch and screen update

                    test_img = self.capture_window(hwnd)
                    test_text = self.extract_text_from_image(test_img) if test_img else ""

                    if test_text != initial_text:
                        # Left works!
                        direction_key = VK_LEFT
                        direction_name = "Left"
                        print(f"[INFO] Left navigation works, continuing...")

                        # Check if we found it
                        if "don't ask again" in test_text.lower() or "yes, and don" in test_text.lower():
                            print(f"[INFO] Found target after 1 Left!")
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
                        time.sleep(0.3)  # Wait for tab switch and screen update
                        presses_count += 1

                        new_img = self.capture_window(hwnd)
                        new_text = self.extract_text_from_image(new_img) if new_img else ""

                        # Check if we found the target
                        if "don't ask again" in new_text.lower() or "yes, and don" in new_text.lower():
                            print(f"[INFO] Found target after {presses_count} {direction_name} presses!")
                            win32api.keybd_event(VK_RETURN, 0, 0, 0)
                            time.sleep(0.05)
                            win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                            found = True
                            break

                        # If content didn't change, reached the end
                        if new_text == initial_text:
                            print(f"[INFO] Reached end in {direction_name} direction after {presses_count} presses")
                            break

                        initial_text = new_text

                    # If not found, go back to start and try opposite direction
                    if not found:
                        print(f"[INFO] Going back to start to try opposite direction...")

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
                            time.sleep(0.3)  # Wait for tab switch

                        print(f"[INFO] Now trying {opposite_name} direction...")

                        # Capture initial again
                        initial_img = self.capture_window(hwnd)
                        initial_text = self.extract_text_from_image(initial_img) if initial_img else ""

                        # Try opposite direction
                        for i in range(6):
                            win32api.keybd_event(VK_MENU, 0, 0, 0)
                            time.sleep(0.05)
                            win32api.keybd_event(opposite_key, 0, 0, 0)
                            time.sleep(0.05)
                            win32api.keybd_event(opposite_key, 0, win32con.KEYEVENTF_KEYUP, 0)
                            time.sleep(0.05)
                            win32api.keybd_event(VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                            time.sleep(0.3)  # Wait for tab switch and screen update

                            new_img = self.capture_window(hwnd)
                            new_text = self.extract_text_from_image(new_img) if new_img else ""

                            # Check if we found the target
                            if "don't ask again" in new_text.lower() or "yes, and don" in new_text.lower():
                                print(f"[INFO] Found target after {i+1} {opposite_name} presses!")
                                win32api.keybd_event(VK_RETURN, 0, 0, 0)
                                time.sleep(0.05)
                                win32api.keybd_event(VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
                                found = True
                                break

                            # If content didn't change, reached the end
                            if new_text == initial_text:
                                print(f"[INFO] Reached end in {opposite_name} direction, no more options")
                                break

                            initial_text = new_text

                        # Still not found, fallback
                        if not found:
                            print(f"[INFO] Exhausted both directions, sending '2' as fallback")
                            win32api.keybd_event(ord('2'), 0, 0, 0)
                            time.sleep(0.05)
                            win32api.keybd_event(ord('2'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_approval_per_window[hwnd] = time.time()

            timestamp = time.strftime('%H:%M:%S')
            try:
                safe_title = window_title.encode('ascii', 'ignore').decode('ascii')
                print(f"[{timestamp}] Auto-approved: {safe_title[:50]}")
            except:
                print(f"[{timestamp}] Auto-approved (window with special chars)")

            # Return to original window
            if self.current_hwnd:
                time.sleep(0.2)
                try:
                    win32gui.SetForegroundWindow(self.current_hwnd)
                except:
                    pass

            return True

        except Exception as e:
            print(f"[ERROR] Auto-approval failed: {e}")
            return False

    def monitor_loop(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("OCR Auto Approver")
        print("="*60)
        print("\nMonitoring all windows via screen OCR...")
        print("Will auto-input '1' when approval request detected")
        print(f"Approval interval: {self.min_approval_interval} seconds")
        print("\nPress Ctrl+C to stop\n")

        while self.running:
            try:
                # Find target windows
                windows = self.find_target_windows()

                # Check each window (max 5)
                for window in windows[:5]:
                    hwnd = window['hwnd']
                    title = window['title']

                    # Capture window
                    img = self.capture_window(hwnd)
                    if not img:
                        continue

                    # OCR text extraction
                    text = self.extract_text_from_image(img)

                    # Check approval pattern
                    if self.check_approval_pattern(text):
                        # Check if should approve
                        if self.should_approve(hwnd):
                            try:
                                safe_title = title.encode('ascii', 'ignore').decode('ascii')
                                print(f"\n[DETECTED] Approval request in: {safe_title[:50]}")
                            except:
                                print(f"\n[DETECTED] Approval request detected")

                            self.send_approval(hwnd, title)

                time.sleep(3)  # OCR is slow, check every 3 seconds

            except Exception as e:
                print(f"[ERROR] Monitoring error: {e}")
                time.sleep(3)

        print("\n[INFO] Monitoring stopped")

    def start(self):
        """Start monitoring"""
        if self.running:
            print("[WARNING] Already running")
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("[OK] OCR Auto Approver started")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        print("[INFO] Monitoring stopped")


def main():
    print("=" * 70)
    print("OCR-based Claude Auto Approver")
    print("=" * 70)
    print()
    print("Features:")
    print("  - Monitors all visible windows via screen OCR")
    print("  - Detects approval prompts from Claude Code")
    print("  - Auto-inputs '1' (NO Enter key)")
    print("  - Shows notifications")
    print()
    print("Requirements:")
    print("  - Tesseract OCR must be installed")
    print("  - Windows must be visible (not minimized)")
    print()
    print("Exit: Ctrl+C")
    print("=" * 70)
    print()

    approver = OCRAutoApprover()

    try:
        # Check target windows
        windows = approver.find_target_windows()
        if windows:
            print(f"\nFound {len(windows)} windows to monitor")
        else:
            print("\n[WARNING] No windows found to monitor")

        approver.start()

        # Main thread wait
        while approver.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        approver.stop()
        print(f"\n[STATS] Total auto-approvals: {approver.approval_count}")
        print("[INFO] Program terminated")


if __name__ == "__main__":
    main()
