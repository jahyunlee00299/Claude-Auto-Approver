"""
Pystray Tray Service Implementation (SRP: Single Responsibility)
Only handles system tray icon management
"""

import os
import threading
from typing import Optional, Callable
from PIL import Image, ImageDraw

from ...interfaces import ITrayService, TrayConfig

# Pystray import
try:
    import pystray
    from pystray import MenuItem as item
    PYSTRAY_AVAILABLE = True
except ImportError:
    PYSTRAY_AVAILABLE = False


class PystrayTrayService(ITrayService):
    """
    System tray service using pystray
    Implements ITrayService interface (DIP)
    """

    def __init__(self, config: Optional[TrayConfig] = None):
        """
        Initialize tray service

        Args:
            config: TrayConfig instance or None for defaults
        """
        self._config = config or TrayConfig()
        self._icon: Optional[pystray.Icon] = None
        self._thread: Optional[threading.Thread] = None
        self._paused = False

        # Callbacks
        self._pause_callback: Optional[Callable[[], None]] = None
        self._resume_callback: Optional[Callable[[], None]] = None
        self._exit_callback: Optional[Callable[[], None]] = None

        # Stats for display
        self._approval_count = 0

    def start(self) -> bool:
        """
        Start the tray icon

        Returns:
            True if tray icon started successfully
        """
        if not PYSTRAY_AVAILABLE:
            print("[WARNING] pystray not available, skipping tray icon")
            return False

        try:
            # Load or create icon image
            icon_image = self._load_icon_image()

            # Create menu
            menu = self._create_menu()

            # Create tray icon
            self._icon = pystray.Icon(
                self._config.app_name,
                icon_image,
                self._config.tooltip,
                menu
            )

            # Start in background thread
            self._thread = threading.Thread(target=self._run_icon, daemon=True)
            self._thread.start()

            print("[OK] System tray icon started")
            return True

        except Exception as e:
            print(f"[ERROR] Failed to create tray icon: {e}")
            return False

    def stop(self) -> None:
        """Stop and remove the tray icon"""
        if self._icon:
            try:
                self._icon.stop()
            except Exception:
                pass
            self._icon = None
        print("[INFO] Tray icon stopped")

    def update_tooltip(self, text: str) -> None:
        """
        Update tray icon tooltip text

        Args:
            text: New tooltip text
        """
        if self._icon:
            self._icon.title = text

    def update_approval_count(self, count: int) -> None:
        """
        Update approval count for tooltip display

        Args:
            count: Current approval count
        """
        self._approval_count = count
        status = "PAUSED" if self._paused else "Running"
        self.update_tooltip(f"{self._config.app_name} ({status}) - {count} approvals")

    def set_pause_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for pause action"""
        self._pause_callback = callback

    def set_resume_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for resume action"""
        self._resume_callback = callback

    def set_exit_callback(self, callback: Callable[[], None]) -> None:
        """Set callback for exit action"""
        self._exit_callback = callback

    def is_available(self) -> bool:
        """
        Check if tray service is available

        Returns:
            True if pystray is installed
        """
        return PYSTRAY_AVAILABLE

    @property
    def is_paused(self) -> bool:
        """Check if currently paused"""
        return self._paused

    def _load_icon_image(self) -> Image.Image:
        """
        Load icon image from file or create default

        Returns:
            PIL Image for tray icon
        """
        # Try to load from configured path
        if self._config.icon_path and os.path.exists(self._config.icon_path):
            icon_image = Image.open(self._config.icon_path)
            if icon_image.size[0] > 64:
                icon_image = icon_image.resize((64, 64), Image.LANCZOS)
            return icon_image

        # Try common icon paths
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        common_paths = [
            os.path.join(base_dir, "approval_icon_64.png"),
            os.path.join(base_dir, "approval_icon.png"),
        ]

        for path in common_paths:
            if os.path.exists(path):
                icon_image = Image.open(path)
                if icon_image.size[0] > 64:
                    icon_image = icon_image.resize((64, 64), Image.LANCZOS)
                return icon_image

        # Create default icon (green circle with checkmark)
        return self._create_default_icon()

    def _create_default_icon(self) -> Image.Image:
        """
        Create a default icon (green circle with checkmark)

        Returns:
            PIL Image
        """
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Green filled circle
        draw.ellipse([4, 4, 60, 60], fill=(76, 175, 80, 255), outline=(56, 142, 60, 255), width=2)

        # White checkmark
        draw.line([(20, 32), (28, 42), (44, 22)], fill=(255, 255, 255, 255), width=4)

        return img

    def _create_menu(self) -> pystray.Menu:
        """
        Create tray icon menu

        Returns:
            pystray Menu object
        """
        return pystray.Menu(
            item('Status: Running', None, enabled=False),
            item(lambda text: f'Approvals: {self._approval_count}', None, enabled=False),
            pystray.Menu.SEPARATOR,
            item('Pause', self._on_pause, checked=lambda item: self._paused),
            item('Resume', self._on_resume, visible=lambda item: self._paused),
            pystray.Menu.SEPARATOR,
            item('Exit', self._on_exit)
        )

    def _run_icon(self) -> None:
        """Run tray icon (called in background thread)"""
        if self._icon:
            try:
                self._icon.run()
            except Exception as e:
                print(f"[ERROR] Tray icon error: {e}")

    def _on_pause(self, icon, item) -> None:
        """Handle pause menu action"""
        self._paused = True
        print("[INFO] Monitoring PAUSED via tray menu")
        self.update_tooltip(f"{self._config.app_name} (PAUSED)")

        if self._pause_callback:
            self._pause_callback()

    def _on_resume(self, icon, item) -> None:
        """Handle resume menu action"""
        self._paused = False
        print("[INFO] Monitoring RESUMED via tray menu")
        self.update_tooltip(f"{self._config.app_name} (Running)")

        if self._resume_callback:
            self._resume_callback()

    def _on_exit(self, icon, item) -> None:
        """Handle exit menu action"""
        print("[INFO] Exit requested via tray menu")

        if self._exit_callback:
            self._exit_callback()

        self.stop()
