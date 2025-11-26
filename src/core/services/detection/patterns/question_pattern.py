"""
Question Pattern (OCP: Extension of BasePattern)
Detects question patterns like "do you want", "would you like"
"""

from typing import List, Optional

from .base_pattern import BasePattern


class QuestionPattern(BasePattern):
    """
    Pattern for detecting question phrases in approval dialogs
    """

    DEFAULT_KEYWORDS = [
        'do you want',
        'would you like',
        'would you',
    ]

    def __init__(self, keywords: Optional[List[str]] = None, confidence: float = 0.7):
        """
        Initialize question pattern

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
        return "QuestionPattern"
