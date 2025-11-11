import psutil
import os

for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
    try:
        if proc.info['name'] == 'python.exe':
            cmdline = proc.info['cmdline']
            if cmdline and 'ocr_auto_simple.py' in ' '.join(cmdline):
                print(f"Killing PID {proc.info['pid']}: {' '.join(cmdline)}")
                proc.kill()
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

print("Done")
