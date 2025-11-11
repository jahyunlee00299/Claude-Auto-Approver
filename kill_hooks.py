#!/usr/bin/env python3
"""
Kill all keyboard and mouse hooks
"""
import keyboard
import mouse

print("Unhooking all keyboard and mouse listeners...")
try:
    keyboard.unhook_all()
    print("✅ Keyboard hooks removed")
except Exception as e:
    print(f"⚠️ Error removing keyboard hooks: {e}")

try:
    mouse.unhook_all()
    print("✅ Mouse hooks removed")
except Exception as e:
    print(f"⚠️ Error removing mouse hooks: {e}")

print("✅ All hooks removed successfully")
