#!/usr/bin/env python3
"""Stop OCR Auto Approver"""
import os
import subprocess

# Read PID file
pid_file = 'ocr_approver.pid'

if not os.path.exists(pid_file):
    print("[INFO] OCR Auto Approver is not running (no PID file)")
    exit(0)

with open(pid_file, 'r') as f:
    pid = int(f.read().strip())

try:
    # Windows: use taskkill
    if os.name == 'nt':
        result = subprocess.run(['taskkill', '/F', '/PID', str(pid)],
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Stopped OCR Auto Approver (PID: {pid})")
        else:
            print(f"[INFO] Process {pid} not found (already stopped)")
    else:
        os.kill(pid, 15)  # SIGTERM
        print(f"[OK] Stopped OCR Auto Approver (PID: {pid})")

    os.remove(pid_file)
except FileNotFoundError:
    print(f"[INFO] Process {pid} not found (already stopped)")
    if os.path.exists(pid_file):
        os.remove(pid_file)
except Exception as e:
    print(f"[ERROR] Failed to stop: {e}")
