#!/usr/bin/env python3
"""
Claude Auto Approver - Main Entry Point (SOLID Architecture)

This is the main entry point for the refactored SOLID-compliant application.
All dependencies are created through the DependencyContainer.
"""

import sys
import time

from core import DependencyContainer
from config import Settings


def print_banner():
    """Print application banner"""
    print("=" * 70)
    print("OCR-based Claude Auto Approver (SOLID Architecture)")
    print("=" * 70)
    print()
    print("Features:")
    print("  - Monitors all visible windows via screen OCR")
    print("  - Detects approval prompts from Claude Code")
    print("  - Auto-responds with appropriate option")
    print("  - Shows notifications")
    print("  - System tray icon for status and control")
    print()
    print("Architecture:")
    print("  - SRP: Each class has single responsibility")
    print("  - OCP: New patterns can be added without modification")
    print("  - LSP: All services implement interfaces")
    print("  - ISP: Small, focused interfaces")
    print("  - DIP: Dependencies injected through interfaces")
    print()
    print("Requirements:")
    print("  - Tesseract OCR must be installed")
    print("  - Windows must be visible (not minimized)")
    print()
    print("Controls:")
    print("  - Right-click tray icon for menu")
    print("  - Pause/Resume monitoring from tray")
    print("  - Exit: Ctrl+C or tray menu")
    print("=" * 70)
    print()


def main():
    """Main entry point"""
    print_banner()

    # Load settings
    settings = Settings.load()
    print(f"[OK] Settings loaded")
    print(f"[INFO] Tesseract path: {settings.tesseract_path}")
    print(f"[INFO] Scan interval: {settings.scan_interval}s")
    print(f"[INFO] Cooldown: {settings.cooldown_seconds}s")
    print()

    # Create orchestrator through DI container
    try:
        orchestrator = DependencyContainer.create_orchestrator(
            settings=settings,
            use_tray=True
        )
        print("[OK] All services initialized")
    except Exception as e:
        print(f"[ERROR] Failed to initialize services: {e}")
        sys.exit(1)

    try:
        # Start monitoring
        orchestrator.start()

        # Main loop - wait for exit
        while orchestrator.is_running:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n[INFO] Interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
    finally:
        orchestrator.stop()
        print(f"\n[STATS] Total auto-approvals: {orchestrator.approval_count}")
        print("[INFO] Program terminated")


if __name__ == "__main__":
    main()
