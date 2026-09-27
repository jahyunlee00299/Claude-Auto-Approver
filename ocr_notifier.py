#!/usr/bin/env python3
"""
OCR-based Approval Notifier
Detects other terminals' approval requests via screen OCR and shows a notification
"""
import sys
import time
import threading
import win32gui
import win32ui
import win32con
import win32console
import winsound
from PIL import Image
import pytesseract
import io
from winotify import Notification, audio

# No UTF-8 configuration - use ASCII only for output to avoid encoding issues

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class OCRNotifier:
    """OCR-based approval detection and notification"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.notification_count = 0
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
        self.last_notification_per_window = {}
        self.min_notification_interval = 15  # Notify once per 15 seconds per window

        # Current window
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

        print("[OK] OCR Notifier initialized")

    def find_target_windows(self):
        """Find windows to monitor - all visible windows (including the current one)"""
        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:  # Include the current window too
                    # Check exclude keywords
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
        """Capture a window screenshot"""
        try:
            # Get window size
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # Check minimum size
            if width < 100 or height < 100:
                return None

            # Device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Create bitmap
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
            # Only the bottom part of the image (most recent output)
            width, height = img.size
            # Crop only the bottom 30% region
            bottom_region = img.crop((0, int(height * 0.7), width, height))

            # Run OCR
            text = pytesseract.image_to_string(bottom_region, lang='eng')
            return text

        except Exception:
            return ""

    def check_approval_pattern(self, text):
        """Check text for an approval pattern"""
        if not text:
            return False

        text_lower = text.lower()
        for pattern in self.approval_patterns:
            if pattern.lower() in text_lower:
                return True

        return False

    def should_notify(self, hwnd):
        """Check whether a notification should be sent (duplicate prevention)"""
        current_time = time.time()

        # Prevent notifying too often for the same window
        if hwnd in self.last_notification_per_window:
            last_time = self.last_notification_per_window[hwnd]
            if current_time - last_time < self.min_notification_interval:
                return False

        return True

    def show_notification(self, window_title):
        """Show a Windows notification"""
        try:
            # Simplify window title
            if len(window_title) > 50:
                display_title = window_title[:47] + "..."
            else:
                display_title = window_title

            # Create Windows notification
            toast = Notification(
                app_id="Claude Auto Approver",
                title="Approval Request",
                msg=f"Claude Code is waiting for approval in:\n{display_title}",
                duration="long"
            )

            # Set sound
            toast.set_audio(audio.Default, loop=False)

            # Show notification
            toast.show()

            # Also play a system beep
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)

            self.notification_count += 1
            timestamp = time.strftime('%H:%M:%S')
            print(f"[{timestamp}] Notification sent: {display_title}")

        except Exception as e:
            print(f"[WARNING] Notification failed: {e}")
            # Still play the sound even if the notification fails
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except:
                pass

    def monitor_loop(self):
        """Main monitoring loop"""
        print("\n" + "="*60)
        print("OCR-based Approval Notifier")
        print("="*60)
        print("\nMonitoring all windows via screen OCR...")
        print(f"Notification interval: {self.min_notification_interval} seconds")
        print("\nPress Ctrl+C to stop\n")

        while self.running:
            try:
                # Find target windows
                windows = self.find_target_windows()

                # Check each window (up to 5 at a time)
                for window in windows[:5]:
                    hwnd = window['hwnd']
                    title = window['title']

                    # Capture screen
                    img = self.capture_window(hwnd)
                    if not img:
                        continue

                    # Extract text via OCR
                    text = self.extract_text_from_image(img)

                    # Check approval pattern
                    if self.check_approval_pattern(text):
                        # Duplicate check
                        if self.should_notify(hwnd):
                            print(f"\n[DETECTED] Approval request in: {title}")
                            self.show_notification(title)
                            self.last_notification_per_window[hwnd] = time.time()

                time.sleep(3)  # 3 second interval since OCR is slow

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

        print("[OK] OCR Notifier started")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=3)
        print("[INFO] Monitoring stopped")


def main():
    print("=" * 70)
    print("OCR-based Claude Approval Notifier")
    print("=" * 70)
    print()
    print("Features:")
    print("  - Monitors all visible windows via screen OCR")
    print("  - Detects approval prompts from Claude Code")
    print("  - Shows Windows notifications")
    print("  - NO automatic input (notification only)")
    print()
    print("Requirements:")
    print("  - Tesseract OCR must be installed")
    print("  - May have slight delay due to OCR processing")
    print()
    print("Exit: Ctrl+C")
    print("=" * 70)
    print()

    notifier = OCRNotifier()

    try:
        # Check target windows
        windows = notifier.find_target_windows()
        if windows:
            print(f"\nFound {len(windows)} windows to monitor")
        else:
            print("\n[WARNING] No windows found to monitor")

        notifier.start()

        # Wait on main thread
        while notifier.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        notifier.stop()
        print(f"\n[STATS] Total notifications: {notifier.notification_count}")
        print("[INFO] Program terminated")


if __name__ == "__main__":
    main()
