#!/usr/bin/env python3
"""
Claude Auto Approver - SOLID Architecture Entry Point

Usage:
    python run_solid.py

This runs the refactored SOLID-compliant version of the auto approver.
For the legacy version, use: python ocr_auto_approver.py
"""

import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.dirname(__file__))

from src.main_solid import main

if __name__ == "__main__":
    main()
