"""
Tkinter popup test - a notification that reliably shows
"""
import tkinter as tk
from tkinter import messagebox
import time

def show_popup(title, message):
    """Show a Tkinter popup window"""
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    root.attributes('-topmost', True)  # Always show on top

    # Show message box
    messagebox.showinfo(title, message)

    root.destroy()

def show_custom_popup(title, message, duration=3):
    """Custom popup that disappears automatically"""
    root = tk.Tk()
    root.title(title)

    # Set window size and position
    width = 300
    height = 100
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = screen_width - width - 20  # bottom-right
    y = screen_height - height - 60

    root.geometry(f'{width}x{height}+{x}+{y}')
    root.attributes('-topmost', True)  # always on top
    root.overrideredirect(True)  # remove title bar

    # background color
    root.configure(bg='#2d2d2d')

    # message label
    label = tk.Label(
        root,
        text=message,
        bg='#2d2d2d',
        fg='white',
        font=('Arial', 10),
        wraplength=280,
        justify='center'
    )
    label.pack(expand=True, pady=20, padx=10)

    # auto-close after duration seconds
    root.after(duration * 1000, root.destroy)

    root.mainloop()

if __name__ == "__main__":
    print("Tkinter 팝업 테스트 1: 클릭해야 닫히는 팝업")
    show_popup("테스트", "이 팝업이 보이나요?")

    print("\nTkinter 팝업 테스트 2: 3초 후 자동으로 닫히는 팝업")
    print("우측 하단을 확인하세요!")
    show_custom_popup("Claude Auto Approver", "자동 승인 완료!\nOption 2 전송됨", duration=3)

    print("\n테스트 완료!")
