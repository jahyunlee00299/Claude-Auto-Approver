#!/usr/bin/env python3
"""
전체 통합 테스트 - OCR Auto Approver + 승인 대화상자 + 알림
"""
import time
import subprocess
import sys

print("="*70)
print("Full Integration Test")
print("="*70)
print()
print("This test will:")
print("  1. Start OCR Auto Approver in background")
print("  2. Wait 5 seconds for initialization")
print("  3. Show an approval dialog")
print("  4. Verify auto-approval happens")
print("  5. Check that notification appears")
print()
print("Press Ctrl+C to cancel, or wait 3 seconds to start...")
print()

try:
    time.sleep(3)
except KeyboardInterrupt:
    print("\nCancelled by user")
    sys.exit(0)

print("[STEP 1] Starting OCR Auto Approver...")
print("-"*70)

# Start OCR Auto Approver in background
approver_process = subprocess.Popen(
    ['python', 'ocr_auto_approver.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1
)

print("[OK] OCR Auto Approver started (PID: {})".format(approver_process.pid))
print()

print("[STEP 2] Waiting 5 seconds for initialization...")
time.sleep(5)
print("[OK] Initialization complete")
print()

print("[STEP 3] Showing approval dialog...")
print("-"*70)

# Show approval dialog in background
dialog_process = subprocess.Popen(
    ['python', 'show_approval_test.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

print("[OK] Approval dialog started")
print()

print("[STEP 4] Waiting for auto-approval (max 10 seconds)...")
try:
    stdout, stderr = dialog_process.communicate(timeout=10)
    print("-"*70)
    print("Dialog output:")
    print(stdout)
    if stderr:
        print("Dialog errors:")
        print(stderr)
    print("-"*70)

    if "Option 2 was selected" in stdout or "Option 1 was selected" in stdout or "Option 3 was selected" in stdout:
        print("[SUCCESS] Auto-approval detected!")
        print()
        print("[STEP 5] Check Windows notification center for the alert!")
        print("         Title: 'Auto Approval Complete'")
        print("         Message: 'Option 'X' was automatically selected'")
    else:
        print("[WARNING] Could not confirm auto-approval from output")

except subprocess.TimeoutExpired:
    print("[TIMEOUT] Dialog did not close within 10 seconds")
    dialog_process.kill()
except Exception as e:
    print(f"[ERROR] {e}")

print()
print("[CLEANUP] Stopping OCR Auto Approver...")
approver_process.terminate()
try:
    approver_process.wait(timeout=3)
    print("[OK] OCR Auto Approver stopped")
except subprocess.TimeoutExpired:
    approver_process.kill()
    print("[WARNING] Had to force kill OCR Auto Approver")

print()
print("="*70)
print("Integration Test Complete!")
print("="*70)
print()
print("Expected results:")
print("  [X] Approval dialog appeared")
print("  [X] Option was automatically selected")
print("  [X] Notification appeared in Windows notification center")
print()
print("If notification did not appear, check:")
print("  - Windows notification settings")
print("  - Focus Assist settings (should be Off)")
print("  - Winotify is installed: pip install winotify")
print()
