#!/usr/bin/env python3
"""
Test real monitoring scenario - daemon thread running OCR Auto Approver
"""
import sys
sys.path.insert(0, '.')

from ocr_auto_approver import OCRAutoApprover
import subprocess
import threading
import time

print("="*70)
print("Real Monitoring Test - Simulating Actual OCR Auto Approver")
print("="*70)

# Start a Question dialog in background
print("\nStarting Question dialog in background...")
dialog_process = subprocess.Popen([sys.executable, "test_approval_dialog.py"])

time.sleep(2)  # Wait for dialog to open

# Create approver instance
print("Creating OCR Auto Approver instance...")
approver = OCRAutoApprover()

# Start monitoring (this runs in daemon thread just like the real scenario)
print("Starting monitoring in daemon thread...")
approver.start()

print("\n" + "="*70)
print("Monitoring is now running in daemon thread")
print("It should detect the Question window and:")
print("  1. Print detection message")
print("  2. Show Windows notification")
print("  3. Send '2' key")
print("\nWaiting 10 seconds for detection and approval...")
print("="*70 + "\n")

# Wait for monitoring to detect and approve
time.sleep(10)

# Stop monitoring
print("\nStopping monitoring...")
approver.stop()

# Clean up dialog
try:
    dialog_process.terminate()
except:
    pass

print("\n" + "="*70)
print("Test completed!")
print(f"Total approvals: {approver.approval_count}")
print("="*70)
print("\nDid you see the Windows notification appear?")
print("If not, there may be an issue with notifications in daemon threads.")
