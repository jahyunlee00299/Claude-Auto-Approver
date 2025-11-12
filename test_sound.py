"""
Test sound notification
"""
import winsound
import time

print("Testing sound notification...")
print("You should hear 2 beeps!")

# First beep (1000Hz, 200ms)
winsound.Beep(1000, 200)
time.sleep(0.1)

# Second beep (1200Hz, 150ms)
winsound.Beep(1200, 150)

print("Sound test complete!")
