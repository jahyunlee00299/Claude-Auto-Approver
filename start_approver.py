#!/usr/bin/env python3
"""Start OCR Auto Approver"""
import subprocess
import os
import sys

# Check if already running
pid_file = 'ocr_approver.pid'

if os.path.exists(pid_file):
    with open(pid_file, 'r') as f:
        pid = int(f.read().strip())

    try:
        os.kill(pid, 0)  # Check if process exists
        print(f"[INFO] OCR Auto Approver is already running (PID: {pid})")
        print("[INFO] Run 'python stop_approver.py' to stop it first")
        exit(1)
    except ProcessLookupError:
        print("[INFO] Removing stale PID file")
        os.remove(pid_file)

# Start the process
print("[INFO] Starting OCR Auto Approver...")
process = subprocess.Popen(
    [sys.executable, 'ocr_auto_simple.py'],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
    creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
)

# Save PID
with open(pid_file, 'w') as f:
    f.write(str(process.pid))

print(f"[OK] OCR Auto Approver started (PID: {process.pid})")
print("[INFO] Logs: ocr_auto_approver.log")
print("[INFO] Stop: python stop_approver.py")
