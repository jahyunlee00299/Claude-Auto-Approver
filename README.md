# 🤖 Claude Auto Approver

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

An OCR-based intelligent approval system that automatically detects and handles Claude Code approval prompts appearing in any window — PyCharm, CMD, PowerShell, and more.

## ✨ Key Features

### 🔍 Active OCR Monitoring
- **Full window scan**: scans every visible window with OCR every 3 seconds to detect approval requests
- **Background monitoring**: monitors all windows regardless of current focus
- **Multi-monitor support**: monitors windows on all monitors simultaneously

### 🎯 Intelligent Detection
- **OCR-based text analysis**: precisely detects approval prompts using Tesseract OCR
- **Smart pattern matching**: recognizes 22+ patterns such as "Would you like to proceed?" and "Do you want to approve?"
- **Option number validation**: only detects a prompt when option numbers in the form "1."/"1)" and "2."/"2)" are both present

### 🛡️ Safe Filtering
- **System window exclusion**: automatically excludes the Windows Notification Center, taskbar, and other system UI
- **Program filtering**: automatically excludes Chrome, PowerPoint, HWP, Excel, NVIDIA Overlay, and more
- **Time-based re-approval**: the same window can be re-approved after a 10-second cooldown
- **Size validation**: automatically excludes windows below the minimum size

### 💬 Integrated Notification System
- **Windows notifications**: shows a winotify notification on approval completion (with an SMS sound)
- **Detailed information**: includes a preview of the detected text, the option chosen, and window info
- **Detailed logging**: records the approval time, window info, OCR text, and more
- **Custom icon**: customize the notification icon via approval_icon.png

### 🎮 Intelligent Option Selection
- **3 options**: selects Option 2 (usually "Yes, and don't ask again")
- **2 options**: selects Option 1 (the safer one-time approval)

## 🚀 Quick Start

### Prerequisites

#### 1. Install Tesseract OCR (required)

```bash
# Windows
# Download the installer from https://github.com/UB-Mannheim/tesseract/wiki
# Default install path: C:\Program Files\Tesseract-OCR\tesseract.exe
```

After installing, confirm the path:
- Default path: `C:\Program Files\Tesseract-OCR\tesseract.exe`
- If installed to a different path, edit line 23 in `ocr_auto_approver.py`:
  ```python
  pytesseract.pytesseract.tesseract_cmd = r'your\path\tesseract.exe'
  ```

#### 2. Install Python Packages

```bash
# Clone the repository
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Run the main program
python ocr_auto_approver.py
```

### How It Works

#### Active OCR Monitoring
1. **Enumerate all windows**: gets a list of every visible window
2. **Filter**: excludes system windows and windows matching exclude keywords
3. **Capture screenshot**: captures each window's screen
4. **Extract OCR text**: extracts text with Tesseract
5. **Pattern matching**: checks for approval patterns and option numbers (1., 2.)
6. **Auto approve**:
   - Determine the option count (2 vs 3)
   - Send the appropriate key ('1' or '2')
   - Show a Windows notification
7. **Cooldown**: the same window can be re-approved after 10 seconds
8. **Repeat**: repeats the whole process every 3 seconds

### Example Output

```
============================================================
OCR Auto Approver
============================================================

=== ACTIVE OCR MONITORING ===

Mode: Active OCR (All Windows)
  - Scans ALL visible windows with OCR
  - Detects approval dialogs automatically
  - Auto-responds when pattern detected
  - Excludes: Chrome, PowerPoint, HWP, Excel, System windows

Press Ctrl+C to stop

[INFO] Scanning for target windows...
[OK] Found 8 target windows:
  1. MINGW64:/c/Users/<user>/PycharmProjects (1936x1064)
  2. PyCharm 2024.1 - Claude-Auto-Approver (1920x1080)
  3. Python 3.11 (cmd.exe) - ocr_auto_approver.py (800x600)
  ...

[STATUS] Active monitoring | Approvals: 0 | Checks: 125

[DEBUG] Potential approval dialog detected!
[DEBUG] Option 1: 1. yes, proceed once
[DEBUG] Option 2: 2. yes, and don't ask again
[DEBUG] 2 options detected - selecting option 1

======================================================================
[2025-01-14 12:34:56] APPROVAL REQUEST DETECTED (Active Scan)
======================================================================
Window Title: MINGW64:/c/Users/<user>/PycharmProjects/Claude-Auto-Approver
Action: Sending '1'
Detected Text Preview: Do you want to proceed with this action?
1. Yes, proceed once
2. Yes, and don't ask again
======================================================================

[INFO] Executing approval sequence for: MINGW64:/c/Users/<user>...
[INFO] Sending key: '1'
[SUCCESS] Approval completed at 12:34:56
[INFO] Total approvals so far: 1
[INFO] Window added to cooldown list (10s before next approval)
```

## 📋 System Requirements

- **OS**: Windows 10/11
- **Python**: 3.7+
- **Required software**:
  - Tesseract OCR 5.0+ ([download](https://github.com/UB-Mannheim/tesseract/wiki))
- **Required packages**:
  - `pytesseract` - OCR text extraction
  - `Pillow` - image processing
  - `pywin32` - Windows API access
  - `winotify` - Windows notifications

## ⚙️ Configuration and Customization

### Key Settings (ocr_auto_approver.py)

```python
# Cooldown settings (line 203)
self.re_approval_cooldown = 10          # wait time before re-approving the same window (seconds)

# Monitoring interval (line 776)
time.sleep(3)                           # scan interval (seconds) - controls CPU usage

# OCR settings (line 731)
fast_mode=False                         # set to True for faster OCR (reduced accuracy)
```

### Custom Icon Setup

Place an `approval_icon.png` file at the project root to have it shown in Windows notifications:

```bash
# Recommended size: 256x256 pixels
# Format: PNG
cp your_icon.png approval_icon.png
```

### Adding Exclude Keywords

To exclude a specific window from monitoring, add it to the `exclude_keywords` list in `ocr_auto_approver.py`:

```python
# Lines 171-185
self.exclude_keywords = [
    'auto approval complete',  # exclude the notification popup
    'chrome',                  # Chrome browser
    'google chrome',
    'nvidia geforce',          # NVIDIA overlay
    'powerpoint',              # PowerPoint
    'ppt',
    'microsoft powerpoint',
    'hwp',                     # Hangul word processor
    '.hwp',
    'excel',                   # Excel
    'microsoft excel',
    '.xlsx',
    '.xls',
    'your_app_name',          # add yours here
]
```

## 🎯 Detection Patterns

### Approval Patterns (automatically detected phrases)

The program recognizes patterns flexibly using a **question + action combination approach** (lines 145-182):

#### Question Patterns
```
- "do you want"
- "would you like"
- "would you"
```

#### Action Patterns
```
- "to proceed" / "proceed"
- "to approve" / "approve"
- "to create" / "create"
- "to allow" / "allow"
- "select"
- "choose"
```

#### Specific Patterns (exact match)
```
- "select an option"
- "choose an option"
- "yes, and don't ask again"
- "yes, and remember"
- "yes, allow all edits"
- "approve this action"
- "allow this action"
- "grant permission"
- "proceed with"
- "continue with"
- "select one of the following"
- "choose one of the following"
- "no, and tell claude"
- "tell claude what to do differently"
```

**Matching approach:**
1. **Question + action** combination (e.g., "do you want" + "to proceed")
2. **Exact match** on a specific pattern
3. **Fallback**: recognized even with just a question or just an action

**Recognition examples:**
- ✅ "Do you want to proceed?"
- ✅ "Do you want to continue?" (combination match)
- ✅ "Would you like to approve?"
- ✅ "Select an option"

**Important**: pattern matching requires **all** of the following:
- Contains at least one of the patterns above
- The line contains "1." or "1)"
- The line contains "2." or "2)"
- **Recognized even when preceded by special characters such as an arrow (❯)**

### Automatic System Window Exclusion

The following system windows are automatically filtered out (lines 189-201):

```
- Windows.UI.Core.CoreWindow (Notification Center)
- Shell_TrayWnd (taskbar)
- NotifyIconOverflowWindow (system tray)
- ApplicationFrameWindow (UWP app container)
- Windows.Internal.Shell.TabProxyWindow
- ImmersiveLauncher (Start menu)
- MultitaskingViewFrame (Task View)
- ForegroundStaging (system staging window)
- Dwm (Desktop Window Manager)
```

### Response Logic

The program intelligently selects the approval option (lines 507-559):

#### Option Recognition Approach
- **Extracts only the first word**: "1. Yes, proceed once" → "yes"
- **Handles arrows**: "❯ 1. Yes" → find the "1." position → "yes"
- **Flexible formatting**: recognized even when preceded by special characters or whitespace

#### Selection Logic
- **3 options detected** (1, 2, and 3 all present) → **selects Option 2**
  - Usually "Yes, and don't ask again"
  - The most convenient choice (avoids repeated prompts)

- **2 options detected** (only 1 and 2 present) → **selects Option 1**
  - Usually "Yes, proceed once"
  - The safer choice (one-time approval)

**Recognizable formats:**
```
✅ 1. Yes
✅ ❯ 1. Yes (arrow)
✅   1. Yes (whitespace)
✅ } 1. Yes (brace)
✅ * 1. Yes (symbol)
```

## 🔍 Troubleshooting

### Q: Approval isn't being detected

**A:** Check the following:
1. Confirm Tesseract OCR is installed correctly
   ```bash
   tesseract --version
   ```
2. Confirm the window title isn't included in `exclude_keywords`
3. Check the logs for:
   - `[DEBUG] Potential approval dialog detected!` - OCR detected the keyword
   - `[DEBUG] Option detection: has_option_1=True, has_option_2=True` - option numbers detected
   - Approval only runs when both conditions above are satisfied
4. Improve OCR quality:
   - Make the window larger
   - Increase the font size
   - Use a high-contrast theme

### Q: Approval runs on the wrong window

**A:** Try the following:
1. Add the program's keyword to `exclude_keywords`
2. Increase the `re_approval_cooldown` value to widen the re-approval interval
3. Increase the scan interval (increase `time.sleep(3)` at line 776 to a larger value)

### Q: I'm getting a Tesseract error

**A:**
```python
# Check line 23 in ocr_auto_approver.py
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# If the install path differs, update it:
pytesseract.pytesseract.tesseract_cmd = r'your\install\path\tesseract.exe'
```

### Q: Notifications aren't showing

**A:**
1. Check Windows notification settings: Settings → System → Notifications
2. Reinstall winotify: `pip install --upgrade winotify`
3. Confirm the approval_icon.png file is at the project root

### Q: Re-approval is needed but isn't happening

**A:** The program has a time-based re-approval mechanism (lines 201-203):
- The same window can be re-approved after a **10-second cooldown**
- If you need faster re-approval, decrease the `re_approval_cooldown` value
- If you need immediate re-approval, restart the program

## 📁 Project Structure

```
Claude-Auto-Approver/
├── ocr_auto_approver.py        # main OCR auto-approval program
├── approval_icon.png           # notification icon (optional)
├── requirements.txt            # Python dependencies
├── README.md                  # this file
├── test_detection.py          # OCR detection test
├── test_ocr_with_key.py       # combined OCR + key-input test
├── test_key_only.py           # key-input functionality test
└── test_*.py                  # other test scripts
```

## 🧪 Testing

The project includes several test files:

```bash
# OCR detection test (window capture + OCR text check)
python test_detection.py

# Combined OCR + key-input test (full process)
python test_ocr_with_key.py

# Key-input-only test (confirm '1' is typed in Notepad, etc.)
python test_key_only.py

# Background notification test
python test_bg_notification.py

# Check the current window
python check_current_window.py
```

## 📊 Performance and Optimization

### Active OCR Monitoring
- **Scan interval**: 3 seconds (adjustable)
- **OCR processing time**: about 0.3-0.8 seconds per window
- **Concurrent monitoring**: 10-20 windows on average
- **CPU usage**: 10-20% on average (spikes during OCR processing)

### Memory Usage
- **Baseline**: ~80-120MB
- **During OCR processing**: ~150-200MB

### Optimization Tips
1. **Adjust the scan interval**: increase `time.sleep(3)` to reduce CPU usage
2. **Fast OCR mode**: `extract_text_from_image(img, fast_mode=True)` (reduced accuracy)
3. **Add exclude keywords**: prevents monitoring unnecessary windows

## 🔧 Advanced Usage

### Running in the Background

```bash
# Use Task Scheduler to run automatically at Windows startup
# 1. Open Task Scheduler (taskschd.msc)
# 2. Create a new task
# 3. Trigger: at logon
# 4. Action: python.exe, arguments: "path\ocr_auto_approver.py"
```

### Running Only During Certain Hours

```python
# Add to the monitor_loop() function in ocr_auto_approver.py
import datetime

# Run only from 9 AM to 6 PM
current_hour = datetime.datetime.now().hour
if not (9 <= current_hour < 18):
    time.sleep(60)  # wait 1 minute, then check again
    continue
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OCR powered by [Tesseract](https://github.com/tesseract-ocr/tesseract)
- Windows notifications by [winotify](https://github.com/versa-syahptr/winotify)
- Built with Python and love ❤️

## 📞 Contact

- GitHub: [@jahyunlee00299](https://github.com/jahyunlee00299)
- Issues: [GitHub Issues](https://github.com/jahyunlee00299/Claude-Auto-Approver/issues)

## ⚠️ Precautions

- This tool **automatically accepts approval prompts**
- Pause the program before important operations (Ctrl+C)
- Verify the behavior in a test environment on first run
- Use with care in production environments

## 📈 Recent Improvements

### v2.7 (2025-01)
- **Excel exclusion**: Excel windows are now automatically excluded from monitoring
- **Improved filtering**: also filters .xlsx and .xls filename patterns

### v2.6 (2025-01)
- **Arrow format support**: recognizes Claude Code dialogs in the "❯ 1. Yes" format
- **Flexible pattern matching**: recognizes more patterns via question + action combinations
- **First-word extraction**: extracts only "yes" from "1. Yes, proceed once" to avoid OCR errors
- **Special character handling**: recognizes option numbers even when preceded by braces, symbols, etc.

### v2.5 (2025-01)
- **Option-count-based selection**: selects option 2 for 3 options, option 1 for 2 options
- **Time-based re-approval**: allows re-approving the same window after a 10-second cooldown
- **Improved debugging**: real-time logging of OCR text and option detection status
- **Improved notifications**: added an SMS sound and a preview of the detected text
- **Stronger filtering**: excludes more programs such as Chrome, PowerPoint, HWP, etc.

### v2.0
- **Active OCR monitoring**: periodically scans all windows
- **Improved filtering**: system windows, size validation, per-program exclusion
- **Stronger pattern matching**: recognizes 22+ approval patterns
- **Multi-monitor support**: monitors windows on all monitors simultaneously
- **winotify notifications**: detailed native Windows notifications

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=jahyunlee00299/Claude-Auto-Approver&type=Date)](https://star-history.com/#jahyunlee00299/Claude-Auto-Approver&Date)

---

**⭐ If you find this project useful, please consider giving it a star! ⭐**
