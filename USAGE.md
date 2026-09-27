# 📖 Claude Auto Approver Usage Guide

## 🎯 Program Overview

**ocr_auto_approver.py** - an OCR-based intelligent auto-approval system

### Key Features
- 🔍 **Active OCR monitoring**: scans every window every 3 seconds to automatically detect approval requests
- 🎯 **Intelligent option selection**: picks the optimal option based on the option count (3→option 2, 2→option 1)
- 🛡️ **Smart filtering**: automatically excludes Chrome, PowerPoint, and system windows
- 💬 **Integrated notifications**: detailed Windows notifications with an SMS sound
- ⏱️ **Time-based re-approval**: the same window can be re-approved after a 10-second cooldown
- 🖥️ **Multi-monitor**: monitors windows on all monitors simultaneously

---

## 🚀 Quick Start

### 1. Prerequisites

#### Install Tesseract OCR (required)
```bash
# Windows
# Install from https://github.com/UB-Mannheim/tesseract/wiki
# Default path: C:\Program Files\Tesseract-OCR\tesseract.exe
```

Confirm the install:
```bash
tesseract --version
```

If installed to a different path, edit line 23 in `ocr_auto_approver.py`:
```python
pytesseract.pytesseract.tesseract_cmd = r'your\path\tesseract.exe'
```

#### Install Python Packages
```bash
# Clone the repository
git clone https://github.com/jahyunlee00299/Claude-Auto-Approver.git
cd Claude-Auto-Approver

# Install dependencies
pip install -r requirements.txt
```

**Required packages:**
- `pytesseract` - OCR text extraction
- `Pillow` - image processing
- `pywin32` - Windows API access
- `winotify` - Windows notifications

### 2. Basic Run

```bash
python ocr_auto_approver.py
```

### 3. Example Screen

```
============================================================
OCR Auto Approver
============================================================

=== ACTIVE OCR MONITORING ===

Mode: Active OCR (All Windows)
  - Scans ALL visible windows with OCR
  - Detects approval dialogs automatically
  - Auto-responds when pattern detected
  - Excludes: Chrome, PowerPoint, HWP, System windows

Press Ctrl+C to stop

[INFO] Scanning for target windows...
[OK] Found 8 target windows:
  1. MINGW64:/c/Users/<user>/PycharmProjects (1936x1064)
  2. PyCharm 2024.1 - Claude-Auto-Approver (1920x1080)
  ...

[STATUS] Active monitoring | Approvals: 0 | Checks: 33
```

---

## 📋 How It Works

### Active OCR Monitoring Process

```
┌─────────────────────────────────────────────────────────┐
│ 1. Enumerate all windows                                 │
│    → Get a list of every visible window                  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 2. Filter                                                 │
│    → Exclude system windows and exclude-keyword matches  │
│    → Chrome, PowerPoint, HWP, NVIDIA Overlay, etc.        │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 3. Capture screenshot                                     │
│    → Capture each window's screen with BitBlt             │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 4. Extract OCR text                                        │
│    → Extract text with Tesseract OCR                      │
│    → Prioritize the bottom region (approval-dialog area)  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 5. Pattern matching                                        │
│    → Check approval patterns (22 patterns)                │
│    → Check option numbers (1., 2. required)                │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 6. Auto approve                                             │
│    → Determine the option count (2 vs 3)                   │
│    → Send the appropriate key ('1' or '2')                 │
│    → Show a Windows notification                           │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 7. Cooldown                                                 │
│    → The same window can be re-approved after 10 seconds  │
└────────────────────┬────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────────────┐
│ 8. Repeat                                                    │
│    → Wait 3 seconds, then repeat from step 1               │
└─────────────────────────────────────────────────────────┘
```

### Approval Logic

#### Option Recognition Approach
- **Extracts only the first word**: "1. Yes, proceed once" → "yes"
- **Handles arrows**: "❯ 1. Yes" → find the "1." position → "yes"
- **Flexible formatting**: recognized even when preceded by special characters or whitespace

**Recognizable formats:**
```
✅ 1. Yes
✅ ❯ 1. Yes (arrow)
✅   1. Yes (whitespace)
✅ } 1. Yes (brace)
✅ * 1. Yes (symbol)
```

#### Option-Count-Based Selection
- **2 options** (only 1 and 2 present):
  ```
  ❯ 1. Yes                       ← selected ✓
    2. Tell Claude what to do differently
  ```
  → **Selects Option 1** (the safer one-time approval)

- **3 options** (1, 2, and 3 all present):
  ```
  1. Yes, proceed once
  2. Yes, and don't ask again    ← selected ✓
  3. No, and tell Claude what to do differently
  ```
  → **Selects Option 2** (avoids repeated prompts)

---

## 📋 Detection Patterns

### Approval Patterns - Question + Action Combination Approach

The program recognizes a variety of patterns through **flexible combination matching**:

#### Question Patterns
```
✓ "do you want"
✓ "would you like"
✓ "would you"
```

#### Action Patterns
```
✓ "to proceed" / "proceed"
✓ "to approve" / "approve"
✓ "to create" / "create"
✓ "to allow" / "allow"
✓ "select"
✓ "choose"
```

#### Specific Patterns (exact match)
```
✓ "select an option"
✓ "choose an option"
✓ "yes, and don't ask again"
✓ "yes, and remember"
✓ "yes, allow all edits"
✓ "approve this action"
✓ "allow this action"
✓ "grant permission"
✓ "proceed with"
✓ "continue with"
✓ "select one of the following"
✓ "choose one of the following"
✓ "no, and tell claude"
✓ "tell claude what to do differently"
```

### Matching Approach

1. **Question + action combination**: "do you want" + "to proceed" → ✅
2. **Exact pattern match**: "select an option" → ✅
3. **Fallback**: recognized even with just a question or just an action → ✅

**Recognizable examples:**
```
✅ "Do you want to proceed?"
✅ "Do you want to continue?" (combination match)
✅ "Would you like to approve?"
✅ "Would you like to create?"
✅ "Select an option"
✅ "Choose one"
```

### Required Conditions

**All** of the following must be satisfied for approval to run:

1. ✅ Contains at least one of the patterns above
2. ✅ The line contains **"1." or "1)"** (does not need to be at the start of the line)
3. ✅ The line contains **"2." or "2)"** (does not need to be at the start of the line)

**Example - detected:**
```
Do you want to proceed?
1. Yes, proceed once
2. Yes, and don't ask again
```

```
Do you want to proceed?
❯ 1. Yes                         ← OK even with an arrow
  2. Tell Claude what to do differently
```

**Example - not detected:**
```
Some random text with 1. and 2.  # no approval pattern
```

---

## ⚙️ Configuration and Customization

### 1. Adjusting the Cooldown Time

`ocr_auto_approver.py` line 203:
```python
self.re_approval_cooldown = 10  # wait time before re-approving the same window (seconds)
```

**Use cases:**
- `= 5`: faster re-approval (aggressive)
- `= 30`: slower re-approval (conservative)
- `= 0`: immediate re-approval (caution!)

### 2. Adjusting the Scan Interval

`ocr_auto_approver.py` line 776:
```python
time.sleep(3)  # scan interval (seconds)
```

**Use cases:**
- `= 1`: faster detection, higher CPU usage
- `= 5`: slower detection, lower CPU usage
- `= 3`: **recommended (default)**

### 3. OCR Mode Setting

`ocr_auto_approver.py` line 731:
```python
text = self.extract_text_from_image(img, fast_mode=False)
```

**fast_mode options:**
- `False`: **accurate OCR** (recommended, default)
  - Automatic PSM mode selection
  - Scans the full image
  - Processing time: ~0.5-0.8s per window

- `True`: **fast OCR**
  - PSM 6 (single block)
  - Reduced image size (800x600)
  - Scans only the bottom 40%
  - Processing time: ~0.2-0.4s per window
  - **Caution: reduced accuracy!**

### 4. Adding Exclude Keywords

`ocr_auto_approver.py` lines 171-185:
```python
self.exclude_keywords = [
    'auto approval complete',  # notification popup
    'chrome',
    'google chrome',
    'nvidia geforce',
    'powerpoint',
    'ppt',
    'microsoft powerpoint',
    'hwp',
    '.hwp',
    'your_custom_keyword',  # add yours here
]
```

**Use case:**
```python
self.exclude_keywords = [
    # existing keywords...
    'slack',           # exclude the Slack app
    'discord',         # exclude Discord
    'notepad++',       # exclude Notepad++
    'my_app',          # exclude a custom app
]
```

### 5. Custom Icon Setup

Place the file at the project root:
```bash
# Recommended size: 256x256 pixels
# Format: PNG
cp your_icon.png approval_icon.png
```

The custom icon will be shown in notifications.

---

## 🔍 Debugging and Log Interpretation

### Normal Operation Log

```
[STATUS] Active monitoring | Approvals: 0 | Checks: 33
```
- `Approvals`: cumulative approval count
- `Checks`: number of OCR scans (all windows × iterations)

### Potential Approval Detected

```
[DEBUG] Potential approval dialog detected!
[DEBUG] OCR Text Length: 450
[DEBUG] OCR Text (first 10 non-empty lines):
  Do you want to proceed?
  1. Yes, proceed once
  2. Yes, and don't ask again
```
→ an approval keyword was found; option-number validation is in progress

### Option Detection Status

```
[DEBUG] Option detection: has_option_1=True, has_option_2=True
```
- `True, True`: ✅ option numbers detected correctly
- `False, *`: ❌ Option 1 missing
- `*, False`: ❌ Option 2 missing

### Approval Execution

```
======================================================================
[2025-01-14 12:34:56] APPROVAL REQUEST DETECTED (Active Scan)
======================================================================
Window Title: MINGW64:/c/Users/<user>/PycharmProjects
Action: Sending '1'
Detected Text Preview: Do you want to proceed?
1. Yes, proceed once
2. Yes, and don't ask again
======================================================================

[INFO] Executing approval sequence for: MINGW64:/c/Users/<user>...
[INFO] Sending key: '1'
[SUCCESS] Approval completed at 12:34:56
[INFO] Total approvals so far: 1
[INFO] Window added to cooldown list (10s before next approval)
```

---

## 🔧 Troubleshooting

### Q1: Approval isn't being detected

**Causes and fixes:**

1. **Tesseract OCR not installed, or wrong path**
   ```bash
   tesseract --version  # confirm installation
   ```
   → Not installed: [download Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

   → Fix the path: line 23 in `ocr_auto_approver.py`
   ```python
   pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
   ```

2. **Window title is included in the exclude keywords**
   ```python
   # Check lines 171-185
   self.exclude_keywords = [...]
   ```
   → Remove it from the exclude-keyword list

3. **OCR quality issues**
   - ✅ Make the window larger
   - ✅ Increase the font size
   - ✅ Use a high-contrast theme
   - ✅ Bring the window to the foreground

4. **Check the logs**
   ```
   [DEBUG] Potential approval dialog detected!  ← keyword detected
   [DEBUG] has_option_1=True, has_option_2=True  ← option numbers also detected
   ```
   - If the above messages don't appear, OCR isn't reading the text properly
   - If they appear but approval doesn't happen, pattern matching failed

### Q2: Approval runs on the wrong window

**Fixes:**

1. **Add an exclude keyword**
   ```python
   self.exclude_keywords = [
       # existing keywords...
       'unwanted_app',  # add
   ]
   ```

2. **Increase the cooldown time**
   ```python
   self.re_approval_cooldown = 30  # 10 → 30 seconds
   ```

3. **Increase the scan interval**
   ```python
   time.sleep(5)  # 3 → 5 seconds
   ```

### Q3: Re-approval is needed but isn't happening

**Cause:**
- Still within the 10-second cooldown period

**Fixes:**

1. **Shorten the cooldown time**
   ```python
   self.re_approval_cooldown = 5  # 10 → 5 seconds
   ```

2. **Immediate re-approval (caution!)**
   ```python
   self.re_approval_cooldown = 0  # no cooldown
   ```

3. **Restart the program**
   ```bash
   Ctrl+C  # stop
   python ocr_auto_approver.py  # restart
   ```

### Q4: Notifications aren't showing

**Fixes:**

1. **Confirm winotify is installed**
   ```bash
   pip install --upgrade winotify
   ```

2. **Check Windows notification settings**
   - Settings → System → Notifications
   - Confirm notifications are enabled for Python/PowerShell

3. **Check the icon file**
   ```bash
   ls approval_icon.png  # confirm the file exists
   ```

### Q5: OCR isn't reading the text properly

**Causes:**
- Font too small
- Low screen resolution
- Unusual font in use
- Background color too similar to the text color

**Fixes:**

1. **Increase the window size**
   - Maximize the terminal window
   - Set the font size to 14pt or larger

2. **Use a high-contrast theme**
   - Black text on a white background
   - Or white text on a black background

3. **Change the OCR mode**
   ```python
   # Switch to normal mode
   text = self.extract_text_from_image(img, fast_mode=False)
   ```

4. **Run the test script**
   ```bash
   python test_detection.py
   ```
   → Check how OCR is reading the text

### Q6: CPU usage is too high

**Fixes:**

1. **Increase the scan interval**
   ```python
   time.sleep(5)  # 3 → 5 seconds
   ```

2. **Use fast OCR mode**
   ```python
   text = self.extract_text_from_image(img, fast_mode=True)
   ```

3. **Add exclude keywords**
   - Prevents scanning unnecessary windows

---

## 🧪 Testing

### 1. OCR Detection Test

```bash
python test_detection.py
```

**Functionality:**
- Displays a list of all windows
- Captures a screenshot of the selected window
- Shows the extracted OCR text
- Checks whether the approval pattern is detected

**Use scenarios:**
- Confirm OCR is working properly
- Check what text is being extracted
- Confirm the approval pattern is detected properly

### 2. Combined OCR + Key-Input Test

```bash
python test_ocr_with_key.py
```

**Functionality:**
- Select a window
- Extract OCR text
- Check the approval pattern
- Send the '1' key after user confirmation

**Use scenarios:**
- Confirm the whole process works properly
- Confirm the key input is actually delivered

### 3. Key-Input-Only Test

```bash
python test_key_only.py
```

**Functionality:**
- Sends the '1' key 3 times in a row
- Confirms "111" appears in Notepad, etc.

**Use scenarios:**
- Confirm the key-input mechanism itself works
- Test the win32api.keybd_event function

---

## 💡 Advanced Usage

### 1. Running in the Background

#### Windows Task Scheduler
1. Run `taskschd.msc`
2. Create a new task
3. **Trigger**: at logon
4. **Action**:
   - Program: `python.exe`
   - Arguments: `"C:\path\to\ocr_auto_approver.py"`
5. **Settings**: check "Hidden"

#### Python Background Execution
```python
# run_approver_background.py
import subprocess
import sys

subprocess.Popen(
    [sys.executable, 'ocr_auto_approver.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NO_WINDOW
)
```

Run:
```bash
python run_approver_background.py
```

### 2. Running Only During Certain Hours

Modify the `monitor_loop()` function in `ocr_auto_approver.py`:

```python
def monitor_loop(self):
    import datetime

    # ... existing code ...

    while self.running:
        try:
            # Check the time (run only from 9 AM to 6 PM)
            current_hour = datetime.datetime.now().hour
            if not (9 <= current_hour < 18):
                print(f"[INFO] Outside working hours ({current_hour}:00), sleeping...")
                time.sleep(60)  # wait 1 minute
                continue

            # ... existing monitoring code ...
```

### 3. Saving to a Log File

```bash
# Redirect logs to a file
python ocr_auto_approver.py > approver.log 2>&1

# Watch the log in real time (in a separate terminal)
tail -f approver.log

# On Windows
Get-Content approver.log -Wait
```

### 4. Running Multiple Instances (Caution!)

Run multiple instances with different settings:

```bash
# Instance 1: fast scanning
python ocr_auto_approver.py  # default 3 seconds

# Instance 2: specific windows only (requires code modification)
# Set exclude_keywords differently
```

**Caution:** CPU usage will roughly double!

---

## 📊 Performance Optimization

### Current Performance Metrics

| Item | Value | Description |
|------|-----|------|
| Scan interval | 3 sec | adjustable |
| OCR processing time | 0.3-0.8 sec/window | depends on Tesseract |
| Concurrent monitoring | 10-20 windows | varies by system |
| CPU usage | 10-20% | spikes during OCR processing |
| Memory usage | 80-200MB | increases during OCR processing |

### Optimization Tips

#### 1. Reduce CPU Usage
```python
# Increase the scan interval
time.sleep(5)  # 3 → 5 seconds

# Fast OCR mode
text = self.extract_text_from_image(img, fast_mode=True)
```

#### 2. Reduce Memory Usage
```python
# Reduce image size (inside extract_text_from_image)
if width > 800 or height > 600:
    ratio = min(800/width, 600/height)
    new_size = (int(width * ratio), int(height * ratio))
    img = img.resize(new_size, Image.LANCZOS)
```

#### 3. Increase Scan Speed
```python
# Make aggressive use of exclude keywords
self.exclude_keywords = [
    # add all unnecessary apps
    'chrome', 'slack', 'discord', 'spotify', ...
]
```

---

## 📞 Support and Contributing

### Reporting Issues
Please report to GitHub Issues:
https://github.com/jahyunlee00299/Claude-Auto-Approver/issues

**Issue template:**
```
## Description
[Brief description]

## Steps to Reproduce
1. [Step 1]
2. [Step 2]

## Expected Behavior
[What you expected to happen]

## Actual Behavior
[What actually happened]

## Environment
- OS: Windows 10/11
- Python: 3.x
- Tesseract: 5.x

## Logs
[Paste relevant logs]
```

### Contributing
Pull Requests are welcome!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⚠️ Precautions

1. **Risk of auto-approval**
   - This tool automatically accepts all approval requests
   - Stop the program before important operations (`Ctrl+C`)

2. **Possibility of false positives**
   - OCR is not 100% accurate
   - Make active use of exclude keywords

3. **System resources**
   - OCR is CPU-intensive
   - Be careful when running on battery power

4. **Privacy protection**
   - Screen capture is performed continuously
   - Add windows containing sensitive information to the exclude keywords

---

## 📝 License

MIT License - free to use, modify, and distribute

---

**⭐ If you find this project useful, please give it a star! ⭐**
