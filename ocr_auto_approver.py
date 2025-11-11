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
import tkinter as tk
import os

# No UTF-8 configuration - use ASCII only for output to avoid encoding issues

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def show_screen_alert(message, duration=2):
    """Show a translucent alert at the top center of the screen"""
    def create_alert():
        root = tk.Tk()
        root.withdraw()  # Hide main window

        # Create alert window
        alert = tk.Toplevel(root)
        alert.overrideredirect(True)  # Remove window decorations

        # Force always on top with multiple methods
        alert.attributes('-topmost', True)
        alert.attributes('-alpha', 0.95)  # Translucent
        alert.lift()  # Raise to top
        alert.focus_force()  # Force focus

        # Get screen dimensions
        screen_width = alert.winfo_screenwidth()

        # Create label
        label = tk.Label(
            alert,
            text=message,
            font=('Arial', 11, 'bold'),
            bg='#FF5722',  # Orange-red background
            fg='white',
            padx=15,
            pady=8
        )
        label.pack()

        # Update to get actual size
        alert.update_idletasks()

        # Position at top center
        width = alert.winfo_width()
        x = (screen_width - width) // 2
        y = 50  # 50 pixels from top
        alert.geometry(f'+{x}+{y}')

        # Keep forcing topmost
        def keep_on_top():
            try:
                alert.lift()
                alert.attributes('-topmost', True)
            except:
                pass

        # Refresh topmost status every 100ms
        def refresh_topmost():
            keep_on_top()
            if alert.winfo_exists():
                alert.after(100, refresh_topmost)

        refresh_topmost()

        # Auto-close after duration
        alert.after(int(duration * 1000), lambda: (root.quit(), root.destroy()))
        root.mainloop()

    # Run in separate thread to avoid blocking
    thread = threading.Thread(target=create_alert, daemon=True)
    thread.start()


class OCRAutoApprover:
    """OCR-based approval detection and auto-input"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # Approval patterns - simplified for better detection
        self.approval_patterns = [
            'proceed',
            'Yes',
            'Approve',
            'option',
            'Select',
            'ask again',
            'tell Claude',
        ]

        # Exclude keywords (removed 'editor' to allow Claude Code windows)
        self.exclude_keywords = ['readme', '.md', '.txt']

        # Duplicate prevention - track per window
        self.last_approval_per_window = {}
        self.min_approval_interval = 3  # Auto-approve once per 3 seconds per window

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
        """Send '2' to window and show notification"""
        print(f"[INFO] send_approval called for window: {window_title[:50]}")

        try:
            # Show Windows notification with image
            print(f"[INFO] Creating notification...")
            try:
                # Get the icon path
                script_dir = os.path.dirname(os.path.abspath(__file__))
                icon_path = os.path.join(script_dir, 'approval_icon.png')

                # Determine window type/terminal
                window_type = "Unknown"
                title_lower = window_title.lower()
                if 'powershell' in title_lower:
                    window_type = "PowerShell"
                elif 'cmd' in title_lower or 'command' in title_lower:
                    window_type = "CMD"
                elif 'bash' in title_lower or 'mingw' in title_lower:
                    window_type = "Bash/Git"
                elif 'python' in title_lower:
                    window_type = "Python"
                elif 'question' in title_lower:
                    window_type = "Dialog"
                else:
                    # Try to extract app name from title
                    if ' - ' in window_title:
                        window_type = window_title.split(' - ')[-1][:20]
                    else:
                        window_type = window_title[:20]

                toast = Notification(
                    app_id="Claude Auto Approver",
                    title="AUTO APPROVING",
                    msg=f"Window: {window_type}\nTarget: {window_title[:40]}",
                    duration="short",
                    icon=icon_path
                )

                toast.set_audio(audio.Default, loop=False)

                print(f"[INFO] Showing notification now...")

                # Try to show notification multiple times if needed
                try:
                    toast.show()
                    time.sleep(0.1)  # Small delay to ensure it's sent
                except:
                    pass

                safe_window_type = window_type.encode('ascii', 'ignore').decode('ascii')
                print(f"[SUCCESS] Notification sent for window type: {safe_window_type}")
            except Exception as e:
                print(f"[WARNING] Notification failed: {e}")
                import traceback
                traceback.print_exc()

            # Activate window
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.3)  # Window activation delay

            # Simply send '2' to select "Yes, and don't ask again"
            print(f"[INFO] Sending '2' to select option 2")
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

                    # Quick detection: if window title contains approval keywords
                    title_lower = title.lower()
                    quick_detect_keywords = ['question', 'approve', 'confirm', 'permission', 'allow']

                    if any(keyword in title_lower for keyword in quick_detect_keywords):
                        print(f"\n[QUICK-DETECT] Found approval window: {title}")
                        if self.should_approve(hwnd):
                            print(f"[ACTION] Sending approval and showing notification...")
                            self.send_approval(hwnd, title)
                            print(f"[SUCCESS] Approval sent and notification shown")
                        else:
                            print(f"[SKIP] Too soon to approve again (within {self.min_approval_interval}s)")
                        continue

                    # Fallback: OCR detection for other windows
                    # Capture window
                    img = self.capture_window(hwnd)
                    if not img:
                        continue

                    # OCR text extraction
                    text = self.extract_text_from_image(img)

                    # Check approval pattern
                    if self.check_approval_pattern(text):
                        if self.should_approve(hwnd):
                            try:
                                safe_title = title.encode('ascii', 'ignore').decode('ascii')
                                print(f"\n[OCR-DETECT] Approval request in: {safe_title[:50]}")
                            except:
                                print(f"\n[OCR-DETECT] Approval request detected")

                            print(f"[ACTION] Sending approval and showing notification...")
                            self.send_approval(hwnd, title)
                            print(f"[SUCCESS] Approval sent and notification shown")
                        else:
                            print(f"[SKIP] Too soon to approve again (within {self.min_approval_interval}s)")

                # Sleep once after checking all windows (not per window)
                time.sleep(3)

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
