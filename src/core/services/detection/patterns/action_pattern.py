"""
Action Pattern (OCP: Extension of BasePattern)
Detects action patterns like "to proceed", "approve", "allow"
"""

from typing import List, Optional

from .base_pattern import BasePattern


class ActionPattern(BasePattern):
    """
    Pattern for detecting action phrases in approval dialogs
    """

    DEFAULT_KEYWORDS = [
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
    ]

    def __init__(self, keywords: Optional[List[str]] = None, confidence: float = 0.6):
        """
        Initialize action pattern

        Args:
            keywords: Custom keywords or None for defaults
            confidence: Confidence score when matched
        """
        super().__init__(
            keywords=keywords or self.DEFAULT_KEYWORDS,
            confidence=confidence
        )

    @property
    def name(self) -> str:
        return "ActionPattern"
