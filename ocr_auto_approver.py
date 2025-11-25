#!/usr/bin/env python3
"""
OCR Auto Approver - Entry Point

This is the main entry point for the Claude Auto Approver.
Uses SOLID architecture with separate components for each responsibility.

Usage:
    python ocr_auto_approver.py

Components:
    - Config: Configuration management
    - PatternMatcher: Approval pattern detection
    - WindowManager: Window operations (find, capture, activate)
    - OCREngine: Text extraction from images
    - ApprovalSender: Key input and cooldown management
    - NotificationManager: Windows notifications
    - Approver: Main orchestrator
"""
import sys
import time

# Add src to path for imports
import os
sys.path.insert(0, os.path.dirname(__file__))

from src import Approver, Config


def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("OCR-based Claude Auto Approver")
    print("=" * 70)
    print()
    print("Features:")
    print("  - Monitors all visible windows via screen OCR")
    print("  - Detects approval prompts from Claude Code")
    print("  - Auto-inputs '1' or '2' based on options")
    print("  - Shows Windows notifications")
    print()
    print("Architecture: SOLID")
    print("  - Config: Settings management")
    print("  - PatternMatcher: Pattern detection")
    print("  - WindowManager: Window operations")
    print("  - OCREngine: Text extraction")
    print("  - ApprovalSender: Key input")
    print("  - NotificationManager: Notifications")
    print()
    print("Requirements:")
    print("  - Tesseract OCR must be installed")
    print("  - Windows must be visible (not minimized)")
    print()
    print("Exit: Ctrl+C")
    print("=" * 70)
    print()


def main():
    """Main entry point"""
    print_banner()

    # Create approver with default config
    config = Config.default()
    approver = Approver(config=config)

    try:
        # List target windows
        approver.list_windows()

        # Start monitoring
        approver.start()

        # Keep main thread alive
        while approver.running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        approver.stop()
        print(f"\n[STATS] Total auto-approvals: {approver.approval_count}")
        print("[INFO] Program terminated")


if __name__ == "__main__":
    main()
