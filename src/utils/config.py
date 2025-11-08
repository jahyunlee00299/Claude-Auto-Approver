"""
Configuration utilities for Claude Auto Approver
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from file

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        Configuration dictionary
    """
    # Default configuration
    default_config = {
        'auto_approve': True,
        'delay_seconds': 1,
        'safe_mode': True,
        'log_level': 'INFO',
        'patterns': [
            'Do you want to approve',
            'Click OK to continue',
            'Confirm action',
            'Are you sure',
            'Do you want to proceed'
        ]
    }

    if config_path is None:
        # Look for config in common locations
        project_root = Path(__file__).parent.parent.parent
        possible_paths = [
            project_root / 'config.yaml',
            project_root / 'config.yml',
            project_root / 'config.json',
            Path.home() / '.claude-auto-approver' / 'config.yaml'
        ]

        for path in possible_paths:
            if path.exists():
                config_path = str(path)
                break

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                if config_path.endswith('.json'):
                    user_config = json.load(f)
                else:
                    user_config = yaml.safe_load(f) or {}

            # Merge with defaults
            if 'settings' in user_config:
                default_config.update(user_config['settings'])
            if 'patterns' in user_config:
                default_config['patterns'] = user_config['patterns']

            print(f"✅ Loaded configuration from: {config_path}")

        except Exception as e:
            print(f"⚠️ Error loading config: {e}")
            print("Using default configuration...")

    return default_config


def save_config(config: Dict[str, Any], config_path: str = None):
    """
    Save configuration to file

    Args:
        config: Configuration dictionary
        config_path: Path to save configuration file
    """
    if config_path is None:
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / 'config.yaml'

    try:
        config_data = {
            'settings': {k: v for k, v in config.items() if k != 'patterns'},
            'patterns': config.get('patterns', [])
        }

        with open(config_path, 'w') as f:
            yaml.dump(config_data, f, default_flow_style=False)

        print(f"✅ Configuration saved to: {config_path}")

    except Exception as e:
        print(f"❌ Error saving config: {e}")