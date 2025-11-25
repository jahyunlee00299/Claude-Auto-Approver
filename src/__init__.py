"""
Claude Auto Approver - Source Package
"""

from .auto_approver import AutoApprover as Approver
from .utils.config import load_config

# Create a simple Config class for compatibility
class Config:
    """Configuration class"""

    @staticmethod
    def default():
        """Get default configuration"""
        return load_config()

    @staticmethod
    def from_file(path: str):
        """Load configuration from file"""
        return load_config(path)

__all__ = ['Approver', 'Config', 'load_config']
