"""
Claude Auto Approver - Source Package

This package provides two architectures:
1. Legacy: Original monolithic implementation (auto_approver.py)
2. SOLID: Refactored implementation following SOLID principles (core/)

To use the SOLID architecture:
    from src.core import DependencyContainer, ApprovalOrchestrator
    from src.config import Settings

    settings = Settings.load()
    orchestrator = DependencyContainer.create_orchestrator(settings)
    orchestrator.start()
"""

# Legacy imports for backward compatibility
from .auto_approver import AutoApprover as Approver
from .utils.config import load_config

# SOLID architecture imports
from .core import ApprovalOrchestrator, DependencyContainer
from .config import Settings

# Create a simple Config class for compatibility
class Config:
    """Configuration class (Legacy)"""

    @staticmethod
    def default():
        """Get default configuration"""
        return load_config()

    @staticmethod
    def from_file(path: str):
        """Load configuration from file"""
        return load_config(path)

__all__ = [
    # Legacy
    'Approver', 'Config', 'load_config',
    # SOLID
    'ApprovalOrchestrator', 'DependencyContainer', 'Settings',
]
