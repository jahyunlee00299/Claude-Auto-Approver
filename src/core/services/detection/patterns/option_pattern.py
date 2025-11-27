"""
Option Pattern (OCP: Extension of BasePattern)
Detects numbered options (1., 2., 3.) in text
"""

import re
from typing import Tuple, Optional

from .base_pattern import BasePattern


class OptionPattern(BasePattern):
    """
    Pattern for detecting numbered options in approval dialogs
    Looks for "1.", "1)", "2.", "2)", "3.", "3)" patterns
    """

    def __init__(self, confidence: float = 0.5):
        """
        Initialize option pattern

        Args:
            confidence: Base confidence score
        """
        super().__init__(keywords=[], confidence=confidence)
        self._has_option_1 = False
        self._has_option_2 = False
        self._has_option_3 = False

    @property
    def name(self) -> str:
        return "OptionPattern"

    def matches(self, text: str) -> Tuple[bool, float, Optional[str]]:
        """
        Check if text contains numbered options

        Args:
            text: Text to check

        Returns:
            Tuple of (matched, confidence, matched_text)
        """
        if not text:
            return False, 0.0, None

        # Reset state
        self._has_option_1 = False
        self._has_option_2 = False
        self._has_option_3 = False

        # Check each line for option markers
        for line in text.split('\n'):
            line_stripped = line.strip().lower()

            # Match: "1.", "1)" - but not "11.", "21.", etc.
            if '1.' in line_stripped or '1)' in line_stripped:
                if re.search(r'(?:^|[^\d])1[.)]', line_stripped):
                    self._has_option_1 = True

            if '2.' in line_stripped or '2)' in line_stripped:
                if re.search(r'(?:^|[^\d])2[.)]', line_stripped):
                    self._has_option_2 = True

            if '3.' in line_stripped or '3)' in line_stripped:
                if re.search(r'(?:^|[^\d])3[.)]', line_stripped):
                    self._has_option_3 = True

        # Calculate confidence based on options found
        if self._has_option_1 and self._has_option_2:
            # Both option 1 and 2 found - high confidence
            confidence = 0.8
            matched_text = "options 1, 2" + (", 3" if self._has_option_3 else "")
            return True, confidence, matched_text
        elif self._has_option_1 or self._has_option_2:
            # At least one option found - medium confidence
            confidence = 0.5
            options = []
            if self._has_option_1:
                options.append("1")
            if self._has_option_2:
                options.append("2")
            if self._has_option_3:
                options.append("3")
            matched_text = f"option(s) {', '.join(options)}"
            return True, confidence, matched_text

        return False, 0.0, None

    @property
    def has_option_1(self) -> bool:
        """Check if option 1 was found in last match"""
        return self._has_option_1

    @property
    def has_option_2(self) -> bool:
        """Check if option 2 was found in last match"""
        return self._has_option_2

    @property
    def has_option_3(self) -> bool:
        """Check if option 3 was found in last match"""
        return self._has_option_3

    @property
    def option_count(self) -> int:
        """Get number of options found in last match"""
        count = 0
        if self._has_option_1:
            count += 1
        if self._has_option_2:
            count += 1
        if self._has_option_3:
            count += 1
        return count
