#!/usr/bin/env python3
"""
Stdout Monitor - monitors the current terminal's output for auto-approval
Hooks sys.stdout to detect output content
"""
import sys
import time
import threading
import win32api
import win32con
from collections import deque
import io

# UTF-8 setup
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

class StdoutMonitor:
    """Stdout monitoring and auto-response"""

    def __init__(self):
        self.running = False
        self.monitor_thread = None
        self.approval_count = 0

        # Store recent output lines (last 50 lines)
        self.recent_lines = deque(maxlen=50)
        self.line_lock = threading.Lock()

        # Approval patterns
        self.approval_patterns = [
            '1. Yes',
            '1. Approve',
            '1. OK',
            '1) Yes',
            'option (1-',
            'Select (1)',
        ]

        # Duplicate prevention
        self.last_input_time = 0
        self.min_input_interval = 2

        # Store the original stdout
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr

    def write_line(self, text):
        """Store a line"""
        if text and text.strip():
            with self.line_lock:
                self.recent_lines.append(text)

    def check_approval_pattern(self):
        """Check recent output for an approval pattern"""
        with self.line_lock:
            # Only check the last 10 lines
            recent_text = '\n'.join(list(self.recent_lines)[-10:])

        for pattern in self.approval_patterns:
            if pattern.lower() in recent_text.lower():
                return True
        return False

    def send_approval_input(self):
        """Send '1' (no Enter)"""
        try:
            print("\n✅ 승인 패턴 감지! '1' 입력 중...")

            time.sleep(0.2)

            # Send the '1' key
            win32api.keybd_event(ord('1'), 0, 0, 0)
            time.sleep(0.05)
            win32api.keybd_event(ord('1'), 0, win32con.KEYEVENTF_KEYUP, 0)

            self.approval_count += 1
            self.last_input_time = time.time()

            print(f"   → '1' 입력 완료! (총 {self.approval_count}회)")
            return True

        except Exception as e:
            print(f"❌ 입력 실패: {e}")
            return False

    def monitor_loop(self):
        """Monitoring loop"""
        print("🔍 Stdout 모니터링 시작...")

        while self.running:
            try:
                # Duplicate prevention
                if time.time() - self.last_input_time < self.min_input_interval:
                    time.sleep(0.5)
                    continue

                # Check for an approval pattern
                if self.check_approval_pattern():
                    self.send_approval_input()

                time.sleep(0.3)

            except Exception as e:
                print(f"❌ 모니터링 오류: {e}")
                time.sleep(1)

    def start(self):
        """Start monitoring"""
        if self.running:
            return

        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        print("✅ Stdout Monitor 시작됨")

    def stop(self):
        """Stop monitoring"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=2)
        print(f"🛑 Stdout Monitor 중지 (총 {self.approval_count}회 입력)")


class MonitoredStdout:
    """Stdout wrapper"""

    def __init__(self, original, monitor):
        self.original = original
        self.monitor = monitor

    def write(self, text):
        # Write to the original
        self.original.write(text)
        # Store in the monitor
        self.monitor.write_line(text)

    def flush(self):
        self.original.flush()

    def __getattr__(self, name):
        return getattr(self.original, name)


# Global monitor instance
_monitor = None

def start_monitoring():
    """Start monitoring"""
    global _monitor

    if _monitor is not None:
        print("⚠️ 이미 모니터링 중입니다")
        return _monitor

    _monitor = StdoutMonitor()

    # Hook stdout
    sys.stdout = MonitoredStdout(sys.stdout, _monitor)

    # Start monitoring
    _monitor.start()

    return _monitor

def stop_monitoring():
    """Stop monitoring"""
    global _monitor

    if _monitor is None:
        return

    # Restore stdout
    sys.stdout = _monitor.original_stdout

    # Stop monitoring
    _monitor.stop()
    _monitor = None


if __name__ == "__main__":
    print("=" * 70)
    print("🤖 Stdout Monitor - 테스트 모드")
    print("=" * 70)
    print()
    print("이 프로그램을 import하여 사용하세요:")
    print()
    print("  from stdout_monitor import start_monitoring, stop_monitoring")
    print("  ")
    print("  monitor = start_monitoring()")
    print("  # ... 여기서 작업 수행 ...")
    print("  stop_monitoring()")
    print()
    print("=" * 70)
    print()

    # Test
    monitor = start_monitoring()

    print("테스트: 승인 패턴 출력")
    print()
    print("다음 중 선택하세요:")
    print("1. Yes")
    print("2. No")
    print()

    time.sleep(5)

    stop_monitoring()
    print("\n테스트 완료")
