#!/usr/bin/env python3
"""
OCR Auto Approver - OCR로 승인 요청 감지 + 자동 "1" 입력
With System Tray Icon Support
"""
import sys
import time
import threading
import re
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

# System tray icon support
try:
    import pystray
    from pystray import MenuItem as item
    TRAY_AVAILABLE = True
except ImportError:
    TRAY_AVAILABLE = False
    print("[WARNING] pystray not installed. Tray icon disabled. Install with: pip install pystray")

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
                duration="short"  # short (5 sec) or long (25 sec)
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

            # Set sound - use SMS sound which is louder
            toast.set_audio(audio.SMS, loop=False)

            # Show notification
            toast.show()

            # Give Windows time to process the notification
            time.sleep(0.5)

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

    def __init__(self, use_tray=True):
        self.running = False
        self.paused = False  # Pause state for tray menu
        self.monitor_thread = None
        self.approval_count = 0
        self.current_hwnd = None

        # Tray icon support
        self.use_tray = use_tray and TRAY_AVAILABLE
        self.tray_icon = None
        self.tray_thread = None

        # Notification queue - collect notifications during scan, show during rest period
        self.pending_notifications = []

        # Active OCR monitoring - scans all visible windows
        # Tab cycling feature is separate (not implemented here)

        # Approval patterns - split into question and action parts for flexible matching
        # Question patterns (asking for permission)
        self.question_patterns = [
            'do you want',
            'would you like',
            'would you',
        ]

        # Action patterns (what's being asked)
        self.action_patterns = [
            'to proceed',
            'proceed',
            'to approve',
            'approve',
            'to create',
            'create',
            'to allow',
            'allow',
            'select',
            'choose',
        ]

        # Additional specific patterns (exact matches)
        self.specific_patterns = [
            'select an option',
            'choose an option',
            'yes, and don\'t ask again',
            'yes, and remember',
            'yes, allow all edits',
            'approve this action',
            'allow this action',
            'grant permission',
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
            'hancom',  # Exclude Hancom (Korean)
            'hanword',  # Exclude Hanword
            '한글',  # Exclude Hangul (Korean)
            '한컴',  # Exclude Hancom (Korean)
            'excel',  # Exclude Excel
            'microsoft excel',  # Exclude Microsoft Excel
            '.xlsx',  # Exclude Excel files
            '.xls',  # Exclude Excel files
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
        self.re_approval_cooldown = 20  # Seconds before same window can be approved again

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
            from PIL import ImageEnhance, ImageFilter

            # Pre-processing for better OCR
            # Convert to grayscale
            img = img.convert('L')

            # Increase contrast
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(2.0)

            # Sharpen
            img = img.filter(ImageFilter.SHARPEN)

            # Increase size for better OCR (larger text = better recognition)
            width, height = img.size
            if width < 1200:
                scale_factor = 1200 / width
                new_size = (int(width * scale_factor), int(height * scale_factor))
                img = img.resize(new_size, Image.LANCZOS)

            if fast_mode:
                # Fast mode: use PSM 6 (single block) with better settings
                custom_config = r'--psm 6 --oem 3 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,?!():-\' '

                # Only check bottom 60% where approval dialogs usually are
                width, height = img.size
                bottom_region = img.crop((0, int(height * 0.4), width, height))
                text = pytesseract.image_to_string(bottom_region, lang='eng', config=custom_config)
            else:
                # Normal mode: more thorough with better config
                custom_config = r'--psm 6 --oem 3'
                text = pytesseract.image_to_string(img, lang='eng', config=custom_config)

                # If too little text, try bottom half
                if len(text) < 50:
                    width, height = img.size
                    bottom_region = img.crop((0, int(height * 0.5), width, height))
                    text = pytesseract.image_to_string(bottom_region, lang='eng', config=custom_config)

            return text

        except Exception as e:
            return ""

    def check_approval_pattern(self, text):
        """Check if text contains approval pattern - RELAXED detection for better recognition

        Returns:
            bool: True if approval pattern detected, False otherwise
        """
        if not text:
            return False

        text_lower = text.lower()

        # Remove extra whitespace and normalize text
        text_normalized = ' '.join(text_lower.split())

        # RELAXED: Check for option numbers (more flexible)
        # Look for "1" followed by dot/paren and "2" followed by dot/paren anywhere in text
        has_option_1 = False
        has_option_2 = False
        has_numbered_options = False

        for line in text.split('\n'):
            line_stripped = line.strip().lower()

            # More flexible option detection - check if line contains option markers
            # Match: "1.", "1)", or bullet + "1."
            if '1.' in line_stripped or '1)' in line_stripped:
                # Make sure it's not part of a larger number like "11." or "21."
                if re.search(r'(?:^|[^\d])1[.)]', line_stripped):
                    has_option_1 = True

            if '2.' in line_stripped or '2)' in line_stripped:
                if re.search(r'(?:^|[^\d])2[.)]', line_stripped):
                    has_option_2 = True

        # Check if we have at least one option (relaxed from requiring both)
        has_numbered_options = has_option_1 or has_option_2

        # Debug: Show detection status (reduced verbosity)
        if has_numbered_options:
            print(f"[DEBUG] Option detection: has_option_1={has_option_1}, has_option_2={has_option_2}")

        # Check for specific patterns (exact matches)
        for pattern in self.specific_patterns:
            if pattern in text_normalized:
                print(f"[DEBUG] Matched specific pattern: '{pattern}'")
                # If we found a specific pattern AND have numbered options, approve
                if has_numbered_options:
                    return True

        # Check for question + action combination
        has_question = any(q in text_normalized for q in self.question_patterns)
        has_action = any(a in text_normalized for a in self.action_patterns)

        # RELAXED: Accept if we have (question OR action) AND numbered options
        if (has_question or has_action) and has_numbered_options:
            if has_question and has_action:
                matched_q = [q for q in self.question_patterns if q in text_normalized]
                matched_a = [a for a in self.action_patterns if a in text_normalized]
                print(f"[DEBUG] Matched question+action: {matched_q[0]} + {matched_a[0]}")
            elif has_question:
                matched_q = [q for q in self.question_patterns if q in text_normalized]
                print(f"[DEBUG] Matched question: {matched_q[0]}")
            else:
                matched_a = [a for a in self.action_patterns if a in text_normalized]
                print(f"[DEBUG] Matched action: {matched_a[0]}")
            return True

        return False

    def determine_response_key(self, text):
        """Smart option selection based on actual option text content

        Logic:
        - Parse actual text of each option (1., 2., 3.)
        - Score each option based on keywords:
          - "yes" = +10 points
          - "don't ask again" = +5 bonus (permanent approval)
          - "approve/allow" = +10 points
          - "no/type/tell claude" = -100 points (never select)
        - Select highest scoring option

        Returns:
            str: '1', '2', or '3' based on best match
        """
        if not text:
            return '1'

        # Parse options: {option_number: full_option_text}
        options = {}

        for line in text.split('\n'):
            line_stripped = line.strip().lower()

            # Match "1. text", "1) text", "› 1. text" etc.
            for opt_num in ['1', '2', '3']:
                pattern = rf'(?:^|[^\d]){opt_num}[.)]\s*(.+)'
                match = re.search(pattern, line_stripped)
                if match and opt_num not in options:
                    options[opt_num] = match.group(1).strip()

        print(f"[DEBUG] Parsed options: {options}")

        # Score each option
        best_option = '1'  # Default fallback
        best_score = -999

        for opt_num, opt_text in options.items():
            score = 0

            # Positive signals (want to select)
            if 'yes' in opt_text:
                score += 10
            if "don't ask" in opt_text or "dont ask" in opt_text or "don't ask" in opt_text:
                score += 5  # Permanent approval bonus
            if 'approve' in opt_text:
                score += 10
            if 'allow' in opt_text:
                score += 8
            if 'proceed' in opt_text:
                score += 8

            # Negative signals (never select)
            if 'type' in opt_text and 'here' in opt_text:
                score -= 100  # "Type here to tell Claude..."
            if 'tell claude' in opt_text:
                score -= 100
            if 'differently' in opt_text:
                score -= 100
            if opt_text.startswith('no') and 'yes' not in opt_text:
                score -= 100  # Starts with "No"

            print(f"[DEBUG] Option {opt_num}: '{opt_text[:50]}' -> score={score}")

            if score > best_score:
                best_score = score
                best_option = opt_num

        print(f"[DEBUG] Selected option {best_option} (score={best_score})")
        return best_option

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
            # STEP 1: Activate window FIRST
            print(f"[INFO] Activating target window...")
            try:
                win32gui.SetForegroundWindow(hwnd)
            except:
                pass

            time.sleep(0.3)  # Window activation delay

            # STEP 2: Send the appropriate key
            print(f"[INFO] Sending '{response_key}' to select option {response_key}")
            win32api.keybd_event(ord(response_key), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord(response_key), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.approved_windows[hwnd] = time.time()  # Mark this window as approved with timestamp

            # Update tray icon title
            self.update_tray_title()

            timestamp = time.strftime('%H:%M:%S')
            print(f"[SUCCESS] Approval completed at {timestamp}")
            print(f"[INFO] Total approvals so far: {self.approval_count}")
            print(f"[INFO] Window added to cooldown list ({self.re_approval_cooldown}s before next approval)")

            # STEP 3: Return to original window
            if self.current_hwnd:
                time.sleep(0.2)
                try:
                    win32gui.SetForegroundWindow(self.current_hwnd)
                    time.sleep(0.3)  # Wait for window switch to complete
                except:
                    pass

            # STEP 4: Queue notification to show later (during rest period)
            print(f"[INFO] Queueing notification for rest period...")

            # Determine window type
            window_type = "Unknown"
            title_lower = window_title.lower()

            # Anaconda Prompt detection (check first - more specific)
            # Patterns: "Anaconda Prompt", "Anaconda PowerShell Prompt",
            #           "(base) C:\...", "(myenv) C:\...", "Anaconda3"
            if 'anaconda' in title_lower:
                if 'powershell' in title_lower:
                    window_type = "Anaconda PowerShell"
                else:
                    window_type = "Anaconda Prompt"
            # Conda environment pattern: "(base)", "(myenv)", etc.
            elif title_lower.startswith('(') and ')' in title_lower:
                # Extract environment name from "(envname) ..."
                conda_env_match = re.match(r'\(([^)]+)\)', title_lower)
                if conda_env_match:
                    env_name = conda_env_match.group(1)
                    # Check if it looks like a conda environment (not a PID or other)
                    if env_name and not env_name.isdigit() and len(env_name) < 30:
                        window_type = f"Conda ({env_name})"
            elif 'conda' in title_lower:
                window_type = "Conda"
            elif 'powershell' in title_lower:
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

            # Prepare notification data
            notification_timestamp = time.strftime('%H:%M:%S')

            # Prepare detected text preview - show MORE text
            text_preview = ''
            if detected_text:
                lines = [line.strip() for line in detected_text.split('\n') if line.strip()]
                text_preview = '\n'.join(lines[:8])  # Show first 8 lines (increased from 3)
                if len(text_preview) > 400:
                    text_preview = text_preview[:400] + '...'

            # Build notification message - simple format
            if text_preview:
                notification_msg = f"Window: {safe_title[:40]} | {text_preview}"
            else:
                notification_msg = f"Window: {safe_title[:40]} | (No text)"

            # Add to queue
            self.pending_notifications.append({
                'title': "Auto Approval Complete",
                'message': notification_msg,
                'window_info': safe_title[:100],
                'window_type': window_type,
                'timestamp': notification_timestamp,
                'response_key': response_key
            })

            print(f"[SUCCESS] Approval completed at {timestamp}")
            print(f"[SUCCESS] Notification queued - will show during rest period")
            print(f"[SUCCESS] *** APPROVAL COMPLETED - OPTION '{response_key}' SELECTED ***\n")

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
                # Check if paused (via tray menu)
                if self.paused:
                    time.sleep(1)
                    continue

                # Active OCR monitoring - scans all visible windows
                # Show periodic status update (every 30 seconds)
                current_time = time.time()
                if current_time - last_status_time >= 30:
                    print(f"[STATUS] Active monitoring | Approvals: {self.approval_count} | Checks: {active_check_count}")
                    last_status_time = current_time
                    # Update tray tooltip
                    self.update_tray_title()

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
                                        text = self.extract_text_from_image(img, fast_mode=True)  # Use fast mode to reduce CPU usage

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
                                            print(f"\n=== Full Detected Text (first 15 lines) ===")
                                            line_count = 0
                                            for line in text.split('\n'):
                                                if line.strip():
                                                    safe_line = line.strip()[:100]
                                                    try:
                                                        safe_line = safe_line.encode('ascii', 'ignore').decode('ascii')
                                                    except:
                                                        pass
                                                    print(f"  {safe_line}")
                                                    line_count += 1
                                                    if line_count >= 15:
                                                        break
                                            print(f"{'='*70}\n")
                                            self.send_approval(hwnd, title, response_key, detected_text=text)
                    except Exception as e:
                        pass  # Silent fail for individual window

                # SHOW NOTIFICATIONS during rest period (after all window scans complete)
                if self.pending_notifications:
                    print(f"\n[INFO] Window scan complete. Showing {len(self.pending_notifications)} queued notification(s)...")

                    for notification in self.pending_notifications:
                        try:
                            show_notification_popup(
                                notification['title'],
                                notification['message'],
                                window_info=notification['window_info'],
                                duration=3
                            )
                            print(f"[SUCCESS] Notification shown for: {notification['window_type']} at {notification['timestamp']}")
                            print(f"[SUCCESS] Option '{notification['response_key']}' was selected")
                        except Exception as e:
                            print(f"[WARNING] Failed to show notification: {e}")

                    # Clear the queue
                    self.pending_notifications.clear()
                    print(f"[INFO] All notifications shown. Check Windows Action Center!\n")

                # Check every 10 seconds (slower to reduce CPU usage)
                time.sleep(10)

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
        # Stop tray icon
        if self.tray_icon:
            try:
                self.tray_icon.stop()
            except:
                pass
        print("[INFO] Monitoring stopped")

    # ===== TRAY ICON METHODS =====

    def create_tray_icon(self):
        """Create system tray icon"""
        if not TRAY_AVAILABLE:
            print("[WARNING] pystray not available, skipping tray icon")
            return None

        try:
            # Load icon image
            icon_path = os.path.join(os.path.dirname(__file__), "approval_icon_64.png")
            if not os.path.exists(icon_path):
                icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")

            if os.path.exists(icon_path):
                icon_image = Image.open(icon_path)
                # Resize if needed
                if icon_image.size[0] > 64:
                    icon_image = icon_image.resize((64, 64), Image.LANCZOS)
            else:
                # Create a simple green circle icon if no image found
                icon_image = self._create_default_icon()

            # Create menu
            menu = pystray.Menu(
                item('Status: Running', None, enabled=False),
                item(lambda text: f'Approvals: {self.approval_count}', None, enabled=False),
                pystray.Menu.SEPARATOR,
                item('Pause', self._on_pause, checked=lambda item: self.paused),
                item('Resume', self._on_resume, visible=lambda item: self.paused),
                pystray.Menu.SEPARATOR,
                item('Exit', self._on_exit)
            )

            # Create tray icon
            self.tray_icon = pystray.Icon(
                "Claude Auto Approver",
                icon_image,
                "Claude Auto Approver",
                menu
            )

            print("[OK] System tray icon created")
            return self.tray_icon

        except Exception as e:
            print(f"[ERROR] Failed to create tray icon: {e}")
            return None

    def _create_default_icon(self):
        """Create a default icon (green circle) if no icon file exists"""
        # Create a 64x64 image with a green circle
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Green filled circle
        draw.ellipse([4, 4, 60, 60], fill=(76, 175, 80, 255), outline=(56, 142, 60, 255), width=2)
        # White checkmark
        draw.line([(20, 32), (28, 42), (44, 22)], fill=(255, 255, 255, 255), width=4)
        return img

    def _on_pause(self, icon, item):
        """Pause monitoring"""
        self.paused = True
        print("[INFO] Monitoring PAUSED via tray menu")
        # Update icon tooltip
        if self.tray_icon:
            self.tray_icon.title = "Claude Auto Approver (PAUSED)"
        show_notification_popup("Auto Approver", "Monitoring paused")

    def _on_resume(self, icon, item):
        """Resume monitoring"""
        self.paused = False
        print("[INFO] Monitoring RESUMED via tray menu")
        # Update icon tooltip
        if self.tray_icon:
            self.tray_icon.title = "Claude Auto Approver"
        show_notification_popup("Auto Approver", "Monitoring resumed")

    def _on_exit(self, icon, item):
        """Exit application"""
        print("[INFO] Exit requested via tray menu")
        self.running = False
        if self.tray_icon:
            self.tray_icon.stop()

    def update_tray_title(self):
        """Update tray icon title with current status"""
        if self.tray_icon:
            status = "PAUSED" if self.paused else "Running"
            self.tray_icon.title = f"Claude Auto Approver ({status}) - {self.approval_count} approvals"

    def run_tray_icon(self):
        """Run tray icon in a separate thread"""
        if self.tray_icon:
            try:
                self.tray_icon.run()
            except Exception as e:
                print(f"[ERROR] Tray icon error: {e}")


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
    print("  - System tray icon for status and control")
    print()
    print("Requirements:")
    print("  - Tesseract OCR must be installed")
    print("  - Windows must be visible (not minimized)")
    print()
    print("Controls:")
    print("  - Right-click tray icon for menu")
    print("  - Pause/Resume monitoring from tray")
    print("  - Exit: Ctrl+C or tray menu")
    print("=" * 70)
    print()

    # Check if tray is available
    if TRAY_AVAILABLE:
        print("[OK] System tray support available")
    else:
        print("[WARNING] System tray not available (install pystray: pip install pystray)")

    approver = OCRAutoApprover(use_tray=True)

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

        # Create and start tray icon in background thread
        if approver.use_tray:
            approver.create_tray_icon()
            if approver.tray_icon:
                approver.tray_thread = threading.Thread(target=approver.run_tray_icon, daemon=True)
                approver.tray_thread.start()
                print("[OK] System tray icon started - right-click for menu")

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
