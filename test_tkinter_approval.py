#!/usr/bin/env python3
"""
Test Tkinter popup notification for approval
"""
import tkinter as tk
from tkinter import messagebox
import threading
import time
import winsound

def show_popup_notification(title="승인 완료", message="Claude Code 요청이 자동으로 승인되었습니다", duration=3):
    """
    Show a Tkinter popup notification
    """
    def create_popup():
        # Create root window
        root = tk.Tk()
        root.withdraw()  # Hide the main window

        # Play sound
        try:
            winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS | winsound.SND_ASYNC)
        except:
            pass

        # Create popup window
        popup = tk.Toplevel()
        popup.title(title)

        # Window style
        popup.overrideredirect(True)  # Remove window decorations
        popup.attributes('-topmost', True)  # Always on top
        popup.attributes('-alpha', 0.95)  # Slightly transparent

        # Create frame with border
        frame = tk.Frame(popup, bg='#2b2b2b', highlightbackground='#0084ff', highlightthickness=2)
        frame.pack(padx=2, pady=2, fill='both', expand=True)

        # Title label
        title_label = tk.Label(
            frame,
            text=title,
            font=('Arial', 12, 'bold'),
            fg='white',
            bg='#2b2b2b',
            pady=10,
            padx=20
        )
        title_label.pack()

        # Message label
        msg_label = tk.Label(
            frame,
            text=message,
            font=('Arial', 10),
            fg='#cccccc',
            bg='#2b2b2b',
            pady=5,
            padx=20
        )
        msg_label.pack()

        # Time stamp
        timestamp = time.strftime('%H:%M:%S')
        time_label = tk.Label(
            frame,
            text=f"시간: {timestamp}",
            font=('Arial', 8),
            fg='#999999',
            bg='#2b2b2b',
            pady=10,
            padx=20
        )
        time_label.pack()

        # Position window (bottom-right corner)
        popup.update_idletasks()
        width = popup.winfo_width()
        height = popup.winfo_height()
        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        x = screen_width - width - 50
        y = screen_height - height - 100

        popup.geometry(f'+{x}+{y}')

        # Auto-close after duration
        def close_popup():
            time.sleep(duration)
            popup.destroy()
            root.destroy()

        threading.Thread(target=close_popup, daemon=True).start()

        # Run mainloop
        root.mainloop()

    # Run in thread to not block
    thread = threading.Thread(target=create_popup, daemon=True)
    thread.start()
    return thread

def main():
    print("=" * 60)
    print("Tkinter 승인 팝업 테스트")
    print("=" * 60)
    print()

    # Show multiple popups
    messages = [
        ("자동 승인 완료!", "Claude Code 요청이 승인되었습니다"),
        ("Permission Granted", "Action approved successfully"),
        ("요청 처리 완료", "모든 작업이 자동으로 처리되었습니다")
    ]

    threads = []
    for i, (title, msg) in enumerate(messages):
        print(f"\n[팝업 {i+1}/3] {title}")
        print(f"  메시지: {msg}")

        thread = show_popup_notification(title, msg, duration=5)
        threads.append(thread)

        if i < len(messages) - 1:
            print("  2초 후 다음 팝업...")
            time.sleep(2)

    print("\n[INFO] 팝업창이 화면 오른쪽 하단에 표시됩니다")
    print("[INFO] 5초 후 자동으로 닫힙니다")

    # Wait for all popups to close
    for thread in threads:
        thread.join()

    print("\n[완료] 모든 팝업이 닫혔습니다")

if __name__ == "__main__":
    main()