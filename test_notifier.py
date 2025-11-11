#!/usr/bin/env python3
"""Simple test for approval notifier"""
import sys
import io

# UTF-8 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

print("Testing approval notifier...")

from approval_notifier import ApprovalNotifier
import time

print("Creating notifier...")
notifier = ApprovalNotifier()

print("Starting notifier...")
notifier.start()

print("Waiting 10 seconds...")
time.sleep(10)

print("Stopping...")
notifier.stop()

print("Test complete!")
