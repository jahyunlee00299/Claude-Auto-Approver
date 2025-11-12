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
import subprocess
import os

# No UTF-8 configuration - use ASCII only for output to avoid encoding issues

# Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


def show_notification_popup(title, message, window_info=None, duration=3):
    """
    Show notification using winotify with logo and detailed information
    """
    try:
        # Get current time
        current_time = time.strftime('%Y-%m-%d %H:%M:%S')
        time_only = time.strftime('%H:%M:%S')

        # Build detailed message (use safe ASCII characters only)
        if window_info:
            detailed_message = f"Window: {window_info}\nTime: {current_time}\n\n{message}"
        else:
            detailed_message = f"Time: {current_time}\n\n{message}"

        print(f"[INFO] Notification: {title} at {time_only}")

        # Use winotify for notifications
        try:
            from winotify import Notification, audio
            import os

            # Create notification
            toast = Notification(
                app_id="Claude Auto Approver",
                title=f"✅ {title}",
                msg=detailed_message,
                duration="long"  # short, long
            )

            # Add approval icon if exists
            icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
            if os.path.exists(icon_path):
                try:
                    toast.icon = icon_path
                    print(f"[OK] Approval icon added to notification")
                except Exception as e:
                    print(f"[INFO] Could not add icon to notification: {e}")
            else:
                print(f"[INFO] Icon file not found at {icon_path} - Please save your icon image as approval_icon.png")

            # Set sound
            toast.set_audio(audio.Default, loop=False)

            # Show notification
            toast.show()

            print(f"[OK] Winotify notification sent with detailed info")
            return  # Exit early if winotify succeeds

        except Exception as e:
            print(f"[WARNING] winotify failed: {e}")
            # PowerShell fallback is commented out - use only winotify

        # # PowerShell fallback
        # try:
        #     # Escape XML special characters
        #     title_escaped = unique_title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        #     message_escaped = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        #
        #     # PowerShell script for Windows Toast with Claude Auto Approver branding
        #     ps_script = f'''
        # [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
        # [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
        #
        # $APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'
        #
        # $template = @"
        # <toast scenario='reminder' duration='long'>
        #     <visual>
        #         <binding template='ToastGeneric'>
        #             <text hint-style='header'>{title_escaped}</text>
        #             <text hint-style='body'>{message_escaped}</text>
        #             <text placement='attribution'>Claude Auto Approver</text>
        #         </binding>
        #     </visual>
        #     <audio src='ms-winsoundevent:Notification.IM'/>
        # </toast>
        # "@
        #
        # $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
        # $xml.LoadXml($template)
        # $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
        # $toast.Tag = "approval_${{Get-Random}}"
        # $toast.Group = "ClaudeAutoApprover"
        # [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
        # '''
        #
        #     # Execute PowerShell (non-blocking, best effort)
        #     subprocess.Popen(
        #         ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
        #         stdout=subprocess.DEVNULL,
        #         stderr=subprocess.DEVNULL
        #     )
        #
        #     print(f"[OK] Notification sent to Windows Action Center (Claude Auto Approver)")
        # except:
        #     pass  # Toast is best effort

    except Exception as e:
        print(f"[WARNING] Notification error: {e}")


class OCRAutoApprover:
    """OCR-based approval detection and auto-input"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # Active OCR monitoring - scans all visible windows
        # Tab cycling feature is separate (not implemented here)

        # Approval patterns - sentence-based for more accurate detection
        self.approval_patterns = [
            'would you like to proceed',
            'do you want to proceed',
            'would you like to approve',
            'do you want to approve',
            'do you want to create',
            'do you want to',
            'select an option',
            'choose an option',
            'yes, and don\'t ask again',
            'yes, and remember',
            'yes, allow all edits',
            'approve this action',
            'allow this action',
            'grant permission',
            'would you like to allow',
            'do you want to allow',
            'proceed with',
            'continue with',
            'select one of the following',
            'choose one of the following',
            'no, and tell claude',
            'tell claude what to do differently'
        ]

        # Exclude keywords (removed 'editor' to allow Claude Code windows)
        self.exclude_keywords = [
            'auto approval complete',  # Only exclude notification popups
            'chrome',  # Exclude Chrome browser
            'google chrome',  # Exclude Chrome browser
            'nvidia geforce',  # Exclude NVIDIA overlay
            'program manager',  # Exclude Windows desktop
            'microsoft text input',  # Exclude IME
            'settings',  # Windows settings
            '설정',  # Windows settings (Korean)
            'powerpoint',  # Exclude PowerPoint
            'ppt',  # Exclude PowerPoint files
            'microsoft powerpoint',  # Exclude Microsoft PowerPoint
            'hwp',  # Exclude Hangul word processor
            '.hwp',  # Exclude HWP files
        ]

        # System window class names to exclude
        self.system_classes = [
            'Windows.UI.Core.CoreWindow',  # Windows notification center
            'Shell_TrayWnd',  # Taskbar
            'NotifyIconOverflowWindow',  # System tray
            'Windows.UI.Input.InputSite.WindowClass',  # System UI
            'ApplicationFrameWindow',  # UWP apps container (including notification center)
            'Windows.Internal.Shell.TabProxyWindow',  # Windows Shell
            'ImmersiveLauncher',  # Start menu
            'MultitaskingViewFrame',  # Task view
            'ForegroundStaging',  # System staging window
            'Dwm',  # Desktop Window Manager (notification windows)
        ]

        # Duplicate prevention - track per window with timestamp for time-based re-approval
        self.approved_windows = {}  # Track {hwnd: last_approval_timestamp}
        self.re_approval_cooldown = 10  # Seconds before same window can be approved again

        # Current window
        try:
            self.current_hwnd = win32console.GetConsoleWindow()
        except:
            self.current_hwnd = None

        print("[OK] OCR Auto Approver initialized")
        print(f"[INFO] Mode: Active OCR monitoring (scans all windows)")

    def is_system_window(self, hwnd):
        """Check if window is a system window (notification center, taskbar, etc.)"""
        try:
            # Get window class name
            class_name = win32gui.GetClassName(hwnd)

            # Check if it's a system window class
            if class_name in self.system_classes:
                return True

            # Additional checks for notification-related windows
            if 'notification' in class_name.lower():
                return True
            if 'toast' in class_name.lower():
                return True
            if 'windows.ui' in class_name.lower():
                return True
            if 'xaml' in class_name.lower():  # Windows modern UI
                return True
            if 'dwm' in class_name.lower():  # Desktop Window Manager
                return True

            # Check window style - exclude toolwindows and other non-standard windows
            style = win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE)
            if style & win32con.WS_EX_TOOLWINDOW:  # Tool windows
                return True
            if style & win32con.WS_EX_NOACTIVATE:  # Non-activatable windows
                return True

            # Exclude windows at -32000,-32000 (hidden system windows)
            try:
                left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                if left == -32000 and top == -32000:
                    return True
            except:
                pass

            return False

        except Exception:
            return False

    def find_target_windows(self, verbose=False):
        """Find all visible windows (including current) - with strict filtering

        Works across multiple monitors.

        Args:
            verbose: If True, print detailed debug information
        """
        def callback(hwnd, windows):
            # Check if window is visible OR minimized (we can restore minimized windows)
            if win32gui.IsWindowVisible(hwnd) or win32gui.IsIconic(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if title:
                    # Exclude system windows first
                    if self.is_system_window(hwnd):
                        if verbose:
                            safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
                            print(f"[FILTER] System window: {safe_title}")
                        return True

                    # Exclude keywords
                    title_lower = title.lower()
                    is_excluded = any(exc in title_lower for exc in self.exclude_keywords)

                    if not is_excluded:
                        # Check window size - must be reasonable (not invisible)
                        try:
                            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                            width = right - left
                            height = bottom - top

                            # Minimum size: 100x20 (only exclude invisible windows)
                            # Windows on any monitor will have valid coordinates
                            if width >= 100 and height >= 20:
                                # Get window class to help identify the window type
                                try:
                                    class_name = win32gui.GetClassName(hwnd)
                                except:
                                    class_name = "Unknown"

                                windows.append({
                                    'hwnd': hwnd,
                                    'title': title,
                                    'class': class_name,
                                    'pos': (left, top, right, bottom)
                                })

                                if verbose:
                                    safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
                                    print(f"[TARGET] {safe_title} ({width}x{height})")
                            elif verbose:
                                safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
                                print(f"[FILTER] Too small ({width}x{height}): {safe_title}")
                        except:
                            pass
                    elif verbose:
                        safe_title = title.encode('ascii', 'ignore').decode('ascii')[:40]
                        matching_kw = [k for k in self.exclude_keywords if k in title_lower][0]
                        print(f"[FILTER] Excluded keyword '{matching_kw}': {safe_title}")
            return True

        windows = []
        try:
            win32gui.EnumWindows(callback, windows)
        except:
            pass
        return windows

    def activate_window(self, hwnd):
        """Activate a window (works across multiple monitors)"""
        try:
            # Check if window is minimized
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                time.sleep(0.2)

            # Bring window to front
            win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
            time.sleep(0.1)

            # Try to set foreground - may fail if we don't have permission
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                # Alternative method: simulate Alt key to allow SetForegroundWindow
                win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
                time.sleep(0.05)
                win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(0.05)
                win32gui.SetForegroundWindow(hwnd)

            time.sleep(0.2)  # Wait for window to fully activate

            # Verify window is now in foreground
            current_foreground = win32gui.GetForegroundWindow()
            if current_foreground == hwnd:
                return True
            else:
                print(f"[DEBUG] Failed to bring window to foreground (current: {win32gui.GetWindowText(current_foreground)[:30]})")
                return False

        except Exception as e:
            print(f"[DEBUG] Failed to activate window: {e}")
            return False

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

    def extract_text_from_image(self, img, fast_mode=False):
        """Extract text from image (OCR)

        Args:
            img: PIL Image object
            fast_mode: If True, use faster OCR settings with less accuracy
        """
        try:
            if fast_mode:
                # Fast mode: use PSM 6 (single block) and lower DPI for speed
                custom_config = r'--psm 6 --oem 3'

                # Resize image to smaller size for faster processing
                width, height = img.size
                if width > 800 or height > 600:
                    ratio = min(800/width, 600/height)
                    new_size = (int(width * ratio), int(height * ratio))
                    img = img.resize(new_size, Image.LANCZOS)

                # Only check bottom half where approval dialogs usually are
                width, height = img.size
                bottom_region = img.crop((0, int(height * 0.4), width, height))
                text = pytesseract.image_to_string(bottom_region, lang='eng', config=custom_config)
            else:
                # Normal mode: more thorough
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
        """Check if text contains approval pattern - strict detection to avoid false positives

        Returns:
            bool: True if approval pattern detected, False otherwise
        """
        if not text:
            return False

        text_lower = text.lower()

        # Remove extra whitespace and normalize text
        text_normalized = ' '.join(text_lower.split())

        # STRICT: Must have option numbers in proper format
        has_option_1 = ('1.' in text or '1)' in text) and len([line for line in text.split('\n') if line.strip().startswith(('1.', '1)'))]) > 0
        has_option_2 = ('2.' in text or '2)' in text) and len([line for line in text.split('\n') if line.strip().startswith(('2.', '2)'))]) > 0

        # Debug: Show detection status
        if '1.' in text or '1)' in text or '2.' in text or '2)' in text:
            print(f"[DEBUG] Option detection: has_option_1={has_option_1}, has_option_2={has_option_2}")

        if not (has_option_1 and has_option_2):
            return False  # Must have both option 1 and 2

        # Check for sentence patterns
        for pattern in self.approval_patterns:
            if pattern in text_normalized:
                print(f"[DEBUG] Matched sentence pattern: '{pattern}'")
                return True

        # STRICT check: Must have approval keywords AND proper numbered options
        approval_keywords = ['approve', 'proceed', 'allow', 'select', 'choose', 'permission', 'create', 'want to', 'would you', 'do you']
        has_keyword = any(keyword in text_lower for keyword in approval_keywords)

        if has_keyword and has_option_1 and has_option_2:
            print(f"[DEBUG] Matched approval keyword + numbered options (strict)")
            return True

        return False

    def determine_response_key(self, text):
        """Determine which key to press based on the options in the text

        Logic:
        - If 3 options (1, 2, 3): Select option 2 (usually "yes, and don't ask again")
        - If 2 options (1, 2): Select option 1 (safer, one-time approval)

        Returns:
            str: '1' or '2' depending on the options
        """
        if not text:
            return '1'  # Default to option 1 (safer choice)

        text_lower = text.lower()
        lines = text.split('\n')

        # Extract option texts and count options
        option_1_text = ''
        option_2_text = ''
        option_3_text = ''
        has_option_3 = False

        for line in lines:
            line_stripped = line.strip()
            if line_stripped.startswith('1.') or line_stripped.startswith('1)'):
                option_1_text = line_stripped.lower()
            elif line_stripped.startswith('2.') or line_stripped.startswith('2)'):
                option_2_text = line_stripped.lower()
            elif line_stripped.startswith('3.') or line_stripped.startswith('3)'):
                option_3_text = line_stripped.lower()
                has_option_3 = True

        print(f"[DEBUG] Option 1: {option_1_text[:50] if option_1_text else 'N/A'}")
        print(f"[DEBUG] Option 2: {option_2_text[:50] if option_2_text else 'N/A'}")
        if has_option_3:
            print(f"[DEBUG] Option 3: {option_3_text[:50] if option_3_text else 'N/A'}")
        print(f"[DEBUG] Has 3 options: {has_option_3}")

        # MAIN LOGIC: Check if there are 3 options
        if has_option_3:
            # 3 options detected -> Select option 2 (usually "yes, and don't ask again")
            print(f"[DEBUG] 3 options detected - selecting option 2")
            return '2'
        else:
            # 2 options detected -> Select option 1 (safer, one-time approval)
            print(f"[DEBUG] 2 options detected - selecting option 1")
            return '1'

    def should_approve(self, hwnd):
        """Check if should auto-approve (with time-based cooldown)"""
        # Check if this window was approved before
        if hwnd not in self.approved_windows:
            return True  # Never approved, OK to approve

        # Check if cooldown period has passed
        last_approval_time = self.approved_windows[hwnd]
        time_since_approval = time.time() - last_approval_time

        if time_since_approval >= self.re_approval_cooldown:
            return True  # Cooldown passed, OK to approve again
        else:
            # Still in cooldown period
            remaining = int(self.re_approval_cooldown - time_since_approval)
            return False  # Still in cooldown

    def send_approval(self, hwnd, window_title, response_key, detected_text=''):
        """Send response key to window and show notification

        Args:
            hwnd: Window handle
            window_title: Window title
            response_key: Key to send ('1' or '2') - REQUIRED, no default
            detected_text: OCR detected text (for notification)
        """
        # Convert window title to ASCII-safe string for console output
        try:
            safe_title = window_title.encode('ascii', 'ignore').decode('ascii')
        except:
            safe_title = "Window with special characters"

        print(f"[INFO] Executing approval sequence for: {safe_title[:50]}")
        print(f"[INFO] Sending key: '{response_key}'")

        try:
            # Show Windows notification using winotify
            print(f"[INFO] Creating Windows notification...")

            # Determine window type
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
                if ' - ' in window_title:
                    window_type = window_title.split(' - ')[-1][:20]
                else:
                    window_type = window_title[:20]

            # Show Tkinter popup notification
            try:
                print(f"[INFO] Preparing notification...")
                print(f"[DEBUG] detected_text length: {len(detected_text) if detected_text else 0}")

                # Add timestamp
                timestamp = time.strftime('%H:%M:%S')

                # Prepare detected text preview (first 100 chars, cleaned up)
                text_preview = ''
                if detected_text:
                    # Clean up text: remove extra whitespace, get first few lines
                    lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
                    text_preview = '\n'.join(lines[:3])  # Show first 3 lines
                    if len(text_preview) > 150:
                        text_preview = text_preview[:150] + '...'
                    print(f"[DEBUG] Text preview prepared: {len(text_preview)} chars")
                else:
                    print(f"[WARNING] No detected_text provided to notification!")

                # Build notification message
                notification_msg = f"Option '{response_key}' was automatically selected"
                if text_preview:
                    notification_msg += f"\n\nDetected text:\n{text_preview}"

                print(f"[INFO] Showing popup notification...")

                # Show popup notification (non-blocking)
                show_notification_popup(
                    "Auto Approval Complete",
                    notification_msg,
                    window_info=safe_title[:100],  # Use the full window title
                    duration=5  # Increased to 5 seconds
                )

                # Play system beep for audio feedback
                try:
                    winsound.MessageBeep(winsound.MB_ICONASTERISK)
                    print(f"[OK] Beep played")
                except:
                    pass

                print(f"[SUCCESS] Notification sent for: {window_type} at {timestamp}")
                print(f"[SUCCESS] Check Windows Action Center for notification!")
                print(f"[SUCCESS] *** APPROVAL COMPLETED - OPTION '{response_key}' SELECTED ***")

                # Small delay
                time.sleep(0.2)

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

            # Send the appropriate key
            print(f"[INFO] Sending '{response_key}' to select option {response_key}")
            win32api.keybd_event(ord(response_key), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord(response_key), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.approved_windows[hwnd] = time.time()  # Mark this window as approved with timestamp

            timestamp = time.strftime('%H:%M:%S')
            print(f"[SUCCESS] Approval completed at {timestamp}")
            print(f"[INFO] Total approvals so far: {self.approval_count}")
            print(f"[INFO] Window added to cooldown list ({self.re_approval_cooldown}s before next approval)\n")

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
        print("\n=== ACTIVE OCR MONITORING ===")
        print("\nMode: Active OCR (All Windows)")
        print("  - Scans ALL visible windows with OCR")
        print("  - Detects approval dialogs automatically")
        print("  - Auto-responds when pattern detected")
        print("  - Excludes: Chrome, PowerPoint, HWP, System windows")
        print("\nPress Ctrl+C to stop\n")

        # Show initial window scan
        print("[INFO] Scanning for target windows...")
        initial_windows = self.find_target_windows(verbose=False)
        print(f"[OK] Found {len(initial_windows)} target windows:")
        for i, win in enumerate(initial_windows[:10], 1):  # Show first 10
            safe_title = win['title'].encode('ascii', 'ignore').decode('ascii')[:50]
            width = win['pos'][2] - win['pos'][0]
            height = win['pos'][3] - win['pos'][1]
            print(f"  {i}. {safe_title} ({width}x{height})")
        if len(initial_windows) > 10:
            print(f"  ... and {len(initial_windows) - 10} more")
        print()

        active_check_count = 0
        last_status_time = time.time()

        while self.running:
            try:
                # Active OCR monitoring - scans all visible windows
                # Show periodic status update (every 30 seconds)
                current_time = time.time()
                if current_time - last_status_time >= 30:
                    print(f"[STATUS] Active monitoring | Approvals: {self.approval_count} | Checks: {active_check_count}")
                    last_status_time = current_time

                # Get all target windows
                target_windows = self.find_target_windows(verbose=False)

                # Scan each window
                for win in target_windows:
                    hwnd = win['hwnd']
                    title = win['title']

                    try:
                        # Check if should approve (cooldown check)
                        if hwnd and self.should_approve(hwnd):
                            # Skip system windows and excluded keywords
                            if title and not self.is_system_window(hwnd):
                                title_lower = title.lower()
                                if not any(exc in title_lower for exc in self.exclude_keywords):
                                    # Capture and OCR check
                                    active_check_count += 1
                                    img = self.capture_window(hwnd)
                                    if img:
                                        text = self.extract_text_from_image(img, fast_mode=False)  # Use accurate mode for better detection

                                        # Debug: Print raw OCR text when approval keywords detected
                                        if text and ('do you want' in text.lower() or 'would you' in text.lower() or 'proceed' in text.lower()):
                                            print(f"\n[DEBUG] Potential approval dialog detected!")
                                            print(f"[DEBUG] OCR Text Length: {len(text)}")
                                            print(f"[DEBUG] OCR Text (first 10 non-empty lines):")
                                            line_count = 0
                                            for line in text.split('\n'):
                                                if line.strip():
                                                    print(f"  {line.strip()[:80]}")
                                                    line_count += 1
                                                    if line_count >= 10:
                                                        break

                                        if self.check_approval_pattern(text):
                                            # Determine response key
                                            response_key = self.determine_response_key(text)

                                            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

                                            # Safe title for console output
                                            try:
                                                safe_title = title[:60].encode('ascii', 'ignore').decode('ascii')
                                            except:
                                                safe_title = "Window with special characters"

                                            # Safe text preview
                                            try:
                                                safe_text = text[:200].encode('ascii', 'ignore').decode('ascii')
                                            except:
                                                safe_text = "[text contains special characters]"

                                            print(f"\n{'='*70}")
                                            print(f"[{timestamp}] APPROVAL REQUEST DETECTED (Active Scan)")
                                            print(f"{'='*70}")
                                            print(f"Window Title: {safe_title}")
                                            print(f"Action: Sending '{response_key}'")
                                            print(f"Detected Text Preview: {safe_text}")
                                            print(f"{'='*70}\n")
                                            self.send_approval(hwnd, title, response_key, detected_text=text)
                    except Exception as e:
                        pass  # Silent fail for individual window

                # Check every 3 seconds (slower because we're checking multiple windows)
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
            print(f"\nFound {len(windows)} windows to monitor:")
            for i, win in enumerate(windows, 1):
                title = win['title']
                hwnd = win['hwnd']
                # Convert to ASCII-safe string for console output
                try:
                    safe_title = title.encode('ascii', 'ignore').decode('ascii')
                except:
                    safe_title = "Window with special characters"

                # Get window position to check which monitor
                try:
                    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
                    print(f"  {i}. [{hwnd}] {safe_title[:50]} (pos: {left},{top})")
                except:
                    print(f"  {i}. [{hwnd}] {safe_title[:50]}")
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
