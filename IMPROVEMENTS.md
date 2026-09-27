# OCR Auto Approver - Approval Logic Improvements

## Problems
- Approval requests could be detected even in the Windows Notification Center
- False positives could occur from system UI, small popups, etc.
- Incorrect approvals caused by pattern matching that was too loose

## Improvements

### 1. System Window Filtering (is_system_window)
**Excluded windows:**
- Windows.UI.Core.CoreWindow (Notification Center)
- Shell_TrayWnd (taskbar)
- NotifyIconOverflowWindow (system tray)
- ApplicationFrameWindow (UWP app container)
- Windows.Internal.Shell.TabProxyWindow (Windows shell)
- ImmersiveLauncher (Start menu)
- MultitaskingViewFrame (Task View)
- ForegroundStaging (system staging window)

**Additional validation:**
- Exclude window class names containing 'notification', 'toast', 'windows.ui', 'xaml'
- Exclude windows with the WS_EX_TOOLWINDOW style (tool windows)
- Exclude windows with the WS_EX_NOACTIVATE style (non-activatable windows)

### 2. Window Size Validation
- **Minimum size: 200x100 pixels**
- Excludes small popups or toast notifications

### 3. Stronger Approval Pattern Validation (check_approval_pattern)

#### Method 1: When a Claude keyword is present
- 1 approval pattern + 1 Claude keyword = approve immediately
- Claude keywords: 'claude', 'tool', 'bash', 'edit', 'read', 'write'

#### Method 2: When no Claude keyword is present
- **At least 2 approval indicators are required**
- Approval indicators:
  - contains 'proceed'
  - contains 'approve'
  - contains 'yes'
  - 'option' + ('select' or a digit)
  - contains 'permission' or 'allow'

### 4. Quick Detection Improvements
- **Before:** only checked approval keywords → too loose
- **Now:** requires **both** approval keywords and Claude-related keywords

**Quick-detect keywords:**
- 'question', 'approve', 'confirm', 'permission', 'allow'

**Claude-related keywords:**
- 'claude', 'tool', 'bash', 'edit', 'mingw', 'powershell', 'cmd'

## How to Test

```bash
cd "C:\Users\<user>\PycharmProjects\Claude-Auto-Approver"
python ocr_auto_approver.py
```

## Expected Effects

### ✅ Approved (True Positive)
1. A Bash approval request from Claude Code - 'approve' + 'bash'
2. An approval request in a PowerShell window - 'question' + 'powershell'
3. OCR text: "Proceed with tool execution?" - 'proceed' + 'tool'

### ❌ Not Approved (False Positive Prevention)
1. Windows Notification Center - filtered as a system window
2. A small toast notification (100x50) - filtered by size
3. A generic dialog "Are you sure?" - no Claude keyword + insufficient indicators
4. A browser popup - no Claude-related keyword

## Notes

- **Test on first run**: wait for an actual Claude Code approval request to confirm normal operation
- **Check the logs**: detailed logs are printed on approval (window title, HWND, detection method)
- **Check notifications**: approval history can be checked via Windows notifications

## Troubleshooting

### When approval doesn't trigger
1. Check whether the Claude Code window title contains 'claude', 'tool', 'bash', etc.
2. Check the logs to see whether OCR is reading the text correctly

### When approval triggers incorrectly
1. Add the keyword to exclude to `exclude_keywords` (lines 50-53)
2. Add the window class to exclude to `system_classes` (lines 56-66)
3. Remove overly generic keywords from `claude_keywords` (line 227)
