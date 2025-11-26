"""
Settings Module (SRP: Single Responsibility)
Handles all configuration loading and defaults
"""

import os
import json
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any


@dataclass
class Settings:
    """
    Application settings with sensible defaults
    All configurable values are centralized here
    """

    # Application info
    app_name: str = "Claude Auto Approver"

    # Tesseract configuration
    tesseract_path: str = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    ocr_language: str = 'eng'

    # Timing configuration
    scan_interval: float = 10.0  # Seconds between scans
    cooldown_seconds: float = 20.0  # Seconds before re-approving same window
    activation_delay: float = 0.3  # Seconds after window activation
    key_delay: float = 0.05  # Seconds between key down/up

    # Window filtering
    min_window_width: int = 100
    min_window_height: int = 20

    # Icon path (relative to project root or absolute)
    icon_path: Optional[str] = None

    # Exclude keywords (windows with these in title are ignored)
    exclude_keywords: List[str] = field(default_factory=lambda: [
        'auto approval complete',
        'chrome',
        'google chrome',
        'nvidia geforce',
        'program manager',
        'microsoft text input',
        'settings',
        '설정',
        'powerpoint',
        'ppt',
        'microsoft powerpoint',
        'hwp',
        '.hwp',
        'hancom',
        'hanword',
        '한글',
        '한컴',
        'excel',
        'microsoft excel',
        '.xlsx',
        '.xls',
    ])

    # Question patterns for detection
    question_patterns: List[str] = field(default_factory=lambda: [
        'do you want',
        'would you like',
        'would you',
    ])

    # Action patterns for detection
    action_patterns: List[str] = field(default_factory=lambda: [
        'to proceed',
        'proceed',
        'to approve',
        'approve',
        'to create',
        'create',
        'to allow',
        'allow',
        'select',
        'choose',
    ])

    # Specific patterns for detection
    specific_patterns: List[str] = field(default_factory=lambda: [
        'select an option',
        'choose an option',
        "yes, and don't ask again",
        'yes, and remember',
        'yes, allow all edits',
        'approve this action',
        'allow this action',
        'grant permission',
        'proceed with',
        'continue with',
        'select one of the following',
        'choose one of the following',
        'no, and tell claude',
        'tell claude what to do differently',
    ])

    @classmethod
    def load(cls, config_path: Optional[str] = None) -> 'Settings':
        """
        Load settings from configuration file

        Args:
            config_path: Path to config file (optional)

        Returns:
            Settings instance
        """
        # Start with defaults
        settings = cls()

        # Find config file
        if config_path is None:
            config_path = cls._find_config_file()

        if config_path and os.path.exists(config_path):
            try:
                config_data = cls._load_config_file(config_path)
                settings = cls._merge_config(settings, config_data)
                print(f"[OK] Loaded configuration from: {config_path}")
            except Exception as e:
                print(f"[WARNING] Error loading config: {e}")
                print("[INFO] Using default configuration")

        # Resolve icon path
        settings._resolve_icon_path()

        return settings

    @classmethod
    def _find_config_file(cls) -> Optional[str]:
        """Find configuration file in common locations"""
        # Get project root (assuming this file is in src/config/)
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent

        # Common config paths
        paths = [
            project_root / 'config.yaml',
            project_root / 'config.yml',
            project_root / 'config.json',
            project_root / '.claude-auto-approver.yaml',
            Path.home() / '.claude-auto-approver' / 'config.yaml',
        ]

        for path in paths:
            if path.exists():
                return str(path)

        return None

    @classmethod
    def _load_config_file(cls, path: str) -> Dict[str, Any]:
        """Load config file content"""
        with open(path, 'r', encoding='utf-8') as f:
            if path.endswith('.json'):
                return json.load(f)
            else:
                return yaml.safe_load(f) or {}

    @classmethod
    def _merge_config(cls, settings: 'Settings', config: Dict[str, Any]) -> 'Settings':
        """Merge loaded config into settings"""
        # Handle nested 'settings' key
        if 'settings' in config:
            config = {**config, **config['settings']}

        # Map config keys to settings attributes
        mappings = {
            'app_name': 'app_name',
            'tesseract_path': 'tesseract_path',
            'ocr_language': 'ocr_language',
            'scan_interval': 'scan_interval',
            'cooldown_seconds': 'cooldown_seconds',
            'activation_delay': 'activation_delay',
            'key_delay': 'key_delay',
            'min_window_width': 'min_window_width',
            'min_window_height': 'min_window_height',
            'icon_path': 'icon_path',
            'exclude_keywords': 'exclude_keywords',
            'question_patterns': 'question_patterns',
            'action_patterns': 'action_patterns',
            'specific_patterns': 'specific_patterns',
        }

        for config_key, attr_name in mappings.items():
            if config_key in config:
                setattr(settings, attr_name, config[config_key])

        return settings

    def _resolve_icon_path(self) -> None:
        """Resolve icon path to absolute path"""
        if self.icon_path is None:
            # Try default locations
            project_root = Path(__file__).parent.parent.parent
            default_paths = [
                project_root / 'approval_icon.png',
                project_root / 'approval_icon_64.png',
            ]
            for path in default_paths:
                if path.exists():
                    self.icon_path = str(path)
                    break
        elif not os.path.isabs(self.icon_path):
            # Convert relative to absolute
            project_root = Path(__file__).parent.parent.parent
            self.icon_path = str(project_root / self.icon_path)

    def save(self, config_path: Optional[str] = None) -> None:
        """
        Save settings to configuration file

        Args:
            config_path: Path to save config file
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = str(project_root / 'config.yaml')

        config_data = {
            'settings': {
                'app_name': self.app_name,
                'tesseract_path': self.tesseract_path,
                'ocr_language': self.ocr_language,
                'scan_interval': self.scan_interval,
                'cooldown_seconds': self.cooldown_seconds,
                'activation_delay': self.activation_delay,
                'key_delay': self.key_delay,
                'min_window_width': self.min_window_width,
                'min_window_height': self.min_window_height,
                'icon_path': self.icon_path,
            },
            'exclude_keywords': self.exclude_keywords,
            'question_patterns': self.question_patterns,
            'action_patterns': self.action_patterns,
            'specific_patterns': self.specific_patterns,
        }

        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
            print(f"[OK] Configuration saved to: {config_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save config: {e}")

    def to_dict(self) -> Dict[str, Any]:
        """Convert settings to dictionary"""
        return {
            'app_name': self.app_name,
            'tesseract_path': self.tesseract_path,
            'ocr_language': self.ocr_language,
            'scan_interval': self.scan_interval,
            'cooldown_seconds': self.cooldown_seconds,
            'activation_delay': self.activation_delay,
            'key_delay': self.key_delay,
            'min_window_width': self.min_window_width,
            'min_window_height': self.min_window_height,
            'icon_path': self.icon_path,
            'exclude_keywords': self.exclude_keywords,
            'question_patterns': self.question_patterns,
            'action_patterns': self.action_patterns,
            'specific_patterns': self.specific_patterns,
        }
