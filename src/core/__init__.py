"""
Core module for Claude Auto Approver
SOLID principles applied architecture
"""

from .orchestrator import ApprovalOrchestrator
from .dependency_container import DependencyContainer

__all__ = ['ApprovalOrchestrator', 'DependencyContainer']
