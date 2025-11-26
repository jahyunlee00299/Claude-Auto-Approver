"""
Pattern Detector Interface (OCP: Open/Closed Principle)
Defines contract for approval pattern detection
New patterns can be added without modifying existing code
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, List


@dataclass
class DetectionResult:
    """Result of pattern detection"""
    is_approval: bool
    matched_pattern: Optional[str] = None
    confidence: float = 0.0
    recommended_key: str = '1'
    matched_text: Optional[str] = None
    has_option_1: bool = False
    has_option_2: bool = False
    has_option_3: bool = False

    def __repr__(self) -> str:
        if self.is_approval:
            return f"DetectionResult(is_approval=True, pattern='{self.matched_pattern}', key='{self.recommended_key}')"
        return "DetectionResult(is_approval=False)"


class IPattern(ABC):
    """
    Individual Pattern Interface (OCP: Open for extension)
    Each pattern type implements this interface
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Pattern name for identification"""
        pass

    @abstractmethod
    def matches(self, text: str) -> tuple:
        """
        Check if text matches this pattern

        Args:
            text: Text to check

        Returns:
            Tuple of (matched: bool, confidence: float, matched_text: str)
        """
        pass


class IPatternDetector(ABC):
    """
    Pattern Detector Interface (SRP: Single Responsibility)
    Only handles pattern detection, not execution
    """

    @abstractmethod
    def detect(self, text: str) -> DetectionResult:
        """
        Detect approval patterns in text

        Args:
            text: Text to analyze

        Returns:
            DetectionResult with detection status and recommended action
        """
        pass

    @abstractmethod
    def add_pattern(self, pattern: IPattern) -> None:
        """
        Add a new pattern to the detector (OCP: extension point)

        Args:
            pattern: Pattern instance to add
        """
        pass

    @abstractmethod
    def remove_pattern(self, pattern_name: str) -> bool:
        """
        Remove a pattern by name

        Args:
            pattern_name: Name of pattern to remove

        Returns:
            True if pattern was found and removed
        """
        pass

    @abstractmethod
    def get_patterns(self) -> List[IPattern]:
        """
        Get all registered patterns

        Returns:
            List of registered patterns
        """
        pass
