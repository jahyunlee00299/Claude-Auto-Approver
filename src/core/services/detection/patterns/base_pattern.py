"""
Base Pattern class (OCP: Open/Closed Principle)
Abstract base for all pattern implementations
"""

from abc import ABC, abstractmethod
from typing import Tuple, List, Optional
from dataclasses import dataclass

from ....interfaces import IPattern


@dataclass
class MatchResult:
    """Result of a pattern match"""
    matched: bool
    confidence: float
    matched_text: Optional[str] = None


class BasePattern(IPattern):
    """
    Base class for pattern implementations
    Provides common functionality for keyword-based matching
    """

    def __init__(self, keywords: Optional[List[str]] = None, confidence: float = 0.8):
        """
        Initialize pattern

        Args:
            keywords: List of keywords to match
            confidence: Confidence score when matched (0.0 to 1.0)
        """
        self._keywords = [k.lower() for k in (keywords or [])]
        self._confidence = confidence

    @property
    @abstractmethod
    def name(self) -> str:
        """Pattern name for identification"""
        pass

    def matches(self, text: str) -> Tuple[bool, float, Optional[str]]:
        """
        Check if text matches this pattern

        Args:
            text: Text to check

        Returns:
            Tuple of (matched, confidence, matched_text)
        """
        if not text:
            return False, 0.0, None

        text_lower = text.lower()
        normalized = ' '.join(text_lower.split())

        for keyword in self._keywords:
            if keyword in normalized:
                return True, self._confidence, keyword

        return False, 0.0, None

    def add_keyword(self, keyword: str) -> None:
        """Add a keyword to match list"""
        kw_lower = keyword.lower()
        if kw_lower not in self._keywords:
            self._keywords.append(kw_lower)

    def remove_keyword(self, keyword: str) -> bool:
        """Remove a keyword from match list"""
        kw_lower = keyword.lower()
        if kw_lower in self._keywords:
            self._keywords.remove(kw_lower)
            return True
        return False

    @property
    def keywords(self) -> List[str]:
        """Get list of keywords"""
        return self._keywords.copy()
