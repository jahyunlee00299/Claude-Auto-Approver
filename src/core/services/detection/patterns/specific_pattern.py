"""
Specific Pattern (OCP: Extension of BasePattern)
Detects specific exact phrases for approval dialogs
"""

from typing import List, Optional

from .base_pattern import BasePattern


class SpecificPattern(BasePattern):
    """
    Pattern for detecting specific phrases in approval dialogs
    These are more exact matches with higher confidence
    """

    DEFAULT_KEYWORDS = [
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
    ]

    def __init__(self, keywords: Optional[List[str]] = None, confidence: float = 0.9):
        """
        Initialize specific pattern

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
        return "SpecificPattern"
