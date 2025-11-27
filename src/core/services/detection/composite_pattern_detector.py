"""
Composite Pattern Detector (OCP: Open/Closed Principle)
Combines multiple patterns for comprehensive approval detection
New patterns can be added without modifying this class
"""

from typing import List, Optional

from ...interfaces import IPatternDetector, IPattern, DetectionResult
from .response_analyzer import ResponseAnalyzer
from .patterns import OptionPattern


class CompositePatternDetector(IPatternDetector):
    """
    Composite pattern detector that combines multiple patterns
    Implements IPatternDetector interface (DIP)

    Detection logic:
    1. Check if numbered options exist (required for approval)
    2. Check specific patterns (highest confidence)
    3. Check question + action patterns
    4. Determine appropriate response key
    """

    def __init__(
        self,
        patterns: Optional[List[IPattern]] = None,
        response_analyzer: Optional[ResponseAnalyzer] = None
    ):
        """
        Initialize composite detector

        Args:
            patterns: List of patterns to use (DIP: dependency injection)
            response_analyzer: ResponseAnalyzer instance (DIP: dependency injection)
        """
        self._patterns: List[IPattern] = patterns or []
        self._response_analyzer = response_analyzer or ResponseAnalyzer()
        self._option_pattern: Optional[OptionPattern] = None

        # Find or create option pattern
        for pattern in self._patterns:
            if isinstance(pattern, OptionPattern):
                self._option_pattern = pattern
                break

        if self._option_pattern is None:
            self._option_pattern = OptionPattern()
            self._patterns.append(self._option_pattern)

    def detect(self, text: str) -> DetectionResult:
        """
        Detect approval patterns in text

        Args:
            text: Text to analyze

        Returns:
            DetectionResult with detection status and recommended action
        """
        if not text:
            return DetectionResult(is_approval=False)

        text_lower = text.lower()
        normalized = ' '.join(text_lower.split())

        # Step 1: Check for numbered options (required)
        option_matched, option_confidence, option_text = self._option_pattern.matches(text)

        if not option_matched:
            return DetectionResult(is_approval=False)

        # Step 2: Check all other patterns
        matched_patterns: List[tuple] = []
        for pattern in self._patterns:
            if isinstance(pattern, OptionPattern):
                continue  # Already checked

            matched, confidence, matched_text = pattern.matches(text)
            if matched:
                matched_patterns.append((pattern.name, confidence, matched_text))

        # Step 3: Determine if this is an approval dialog
        if not matched_patterns:
            # Options found but no other patterns
            return DetectionResult(is_approval=False)

        # Step 4: Find best match
        best_match = max(matched_patterns, key=lambda x: x[1])
        pattern_name, confidence, matched_text = best_match

        # Step 5: Analyze response
        response = self._response_analyzer.analyze(text)

        return DetectionResult(
            is_approval=True,
            matched_pattern=pattern_name,
            confidence=confidence,
            recommended_key=response.recommended_key,
            matched_text=matched_text,
            has_option_1=self._option_pattern.has_option_1,
            has_option_2=self._option_pattern.has_option_2,
            has_option_3=self._option_pattern.has_option_3,
        )

    def add_pattern(self, pattern: IPattern) -> None:
        """
        Add a new pattern to the detector (OCP: extension point)

        Args:
            pattern: Pattern instance to add
        """
        # Check for duplicates
        for existing in self._patterns:
            if existing.name == pattern.name:
                return

        self._patterns.append(pattern)

        # Update option pattern reference if needed
        if isinstance(pattern, OptionPattern):
            self._option_pattern = pattern

    def remove_pattern(self, pattern_name: str) -> bool:
        """
        Remove a pattern by name

        Args:
            pattern_name: Name of pattern to remove

        Returns:
            True if pattern was found and removed
        """
        for i, pattern in enumerate(self._patterns):
            if pattern.name == pattern_name:
                # Don't remove option pattern
                if isinstance(pattern, OptionPattern):
                    return False
                self._patterns.pop(i)
                return True
        return False

    def get_patterns(self) -> List[IPattern]:
        """
        Get all registered patterns

        Returns:
            List of registered patterns
        """
        return self._patterns.copy()

    @property
    def pattern_count(self) -> int:
        """Get number of registered patterns"""
        return len(self._patterns)
