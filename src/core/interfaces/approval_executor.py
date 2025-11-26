"""
Approval Executor Interface (ISP: Interface Segregation Principle)
Defines contract for approval execution operations only
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class ExecutionResult:
    """Result of approval execution"""
    success: bool
    key_sent: str
    error_message: Optional[str] = None

    def __repr__(self) -> str:
        if self.success:
            return f"ExecutionResult(success=True, key='{self.key_sent}')"
        return f"ExecutionResult(success=False, error='{self.error_message}')"


class IApprovalExecutor(ABC):
    """
    Approval Executor Interface (SRP: Single Responsibility)
    Only handles sending key inputs to windows
    """

    @abstractmethod
    def send_key(self, hwnd: int, key: str) -> ExecutionResult:
        """
        Send key input to specified window

        Args:
            hwnd: Window handle to send key to
            key: Key to send (e.g., '1', '2', 'enter')

        Returns:
            ExecutionResult with success status
        """
        pass

    @abstractmethod
    def activate_and_send(self, hwnd: int, key: str) -> ExecutionResult:
        """
        Activate window and send key input

        Args:
            hwnd: Window handle
            key: Key to send

        Returns:
            ExecutionResult with success status
        """
        pass
