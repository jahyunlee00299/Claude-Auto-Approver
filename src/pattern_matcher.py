"""
Pattern Matcher for approval detection
SOLID: Single Responsibility - Only handles pattern matching logic
"""
import re
from typing import Optional
from dataclasses import dataclass

from .config import ApprovalPatterns


@dataclass
class MatchResult:
    """Result of pattern matching"""
    is_match: bool
    matched_pattern: Optional[str] = None
    has_option_1: bool = False
    has_option_2: bool = False
    has_option_3: bool = False


class PatternMatcher:
    """Detects approval patterns in OCR text"""

    def __init__(self, patterns: ApprovalPatterns):
        self.patterns = patterns

    def check_approval_pattern(self, text: str) -> MatchResult:
        """
        Check if text contains approval pattern

        Args:
            text: OCR extracted text

        Returns:
            MatchResult with detection details
        """
        if not text:
            return MatchResult(is_match=False)

        text_lower = text.lower()
        text_normalized = ' '.join(text_lower.split())

        # Detect option numbers
        has_option_1 = False
        has_option_2 = False
        has_option_3 = False

        for line in text.split('\n'):
            line_stripped = line.strip().lower()

            if '1.' in line_stripped or '1)' in line_stripped:
                if re.search(r'(?:^|[^\d])1[.)]', line_stripped):
                    has_option_1 = True

            if '2.' in line_stripped or '2)' in line_stripped:
                if re.search(r'(?:^|[^\d])2[.)]', line_stripped):
                    has_option_2 = True

            if '3.' in line_stripped or '3)' in line_stripped:
                if re.search(r'(?:^|[^\d])3[.)]', line_stripped):
                    has_option_3 = True

        has_numbered_options = has_option_1 or has_option_2

        if not has_numbered_options:
            return MatchResult(
                is_match=False,
                has_option_1=has_option_1,
                has_option_2=has_option_2,
                has_option_3=has_option_3
            )

        # Check specific patterns first
        for pattern in self.patterns.specific_patterns:
            if pattern in text_normalized:
                return MatchResult(
                    is_match=True,
                    matched_pattern=pattern,
                    has_option_1=has_option_1,
                    has_option_2=has_option_2,
                    has_option_3=has_option_3
                )

        # Check question + action combination
        has_question = any(q in text_normalized for q in self.patterns.question_patterns)
        has_action = any(a in text_normalized for a in self.patterns.action_patterns)

        if has_question or has_action:
            matched = []
            if has_question:
                matched.extend([q for q in self.patterns.question_patterns if q in text_normalized])
            if has_action:
                matched.extend([a for a in self.patterns.action_patterns if a in text_normalized])

            return MatchResult(
                is_match=True,
                matched_pattern=' + '.join(matched[:2]),
                has_option_1=has_option_1,
                has_option_2=has_option_2,
                has_option_3=has_option_3
            )

        return MatchResult(
            is_match=False,
            has_option_1=has_option_1,
            has_option_2=has_option_2,
            has_option_3=has_option_3
        )

    def determine_response_key(self, text: str) -> str:
        """
        Determine which key to press based on options in text

        Logic:
        - 3 options (1, 2, 3): Select option 2 (usually "yes, and don't ask again")
        - 2 options (1, 2): Select option 1 (safer, one-time approval)

        Args:
            text: OCR extracted text

        Returns:
            '1' or '2' depending on the options
        """
        if not text:
            return '1'

        lines = text.split('\n')
        has_option_3 = False

        for line in lines:
            line_stripped = line.strip().lower()
            if '3.' in line_stripped or '3)' in line_stripped:
                if re.search(r'(?:^|[^\d])3[.)]', line_stripped):
                    has_option_3 = True
                    break

        # 3 options -> select 2, 2 options -> select 1
        return '2' if has_option_3 else '1'

    def extract_option_keywords(self, text: str) -> dict:
        """
        Extract first word after each option number

        Args:
            text: OCR extracted text

        Returns:
            Dictionary with option keywords
        """
        if not text:
            return {}

        lines = text.split('\n')
        options = {}

        for line in lines:
            line_stripped = line.strip().lower()

            for opt_num in ['1', '2', '3']:
                for separator in ['.', ')']:
                    marker = f'{opt_num}{separator}'
                    if marker in line_stripped:
                        pos = line_stripped.index(marker) + 2
                        after_number = line_stripped[pos:].strip()
                        if after_number:
                            first_word = after_number.split(',')[0].split()[0] if after_number.split() else ''
                            options[f'option_{opt_num}'] = first_word
                        break

        return options
