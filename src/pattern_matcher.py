"""
Pattern Matcher for approval detection - Strict Claude Code detection
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
    matched_question: bool = False
    has_option_1_yes: bool = False
    has_option_2_yes: bool = False
    has_option_3_no: bool = False
    debug_info: Optional[str] = None


class PatternMatcher:
    """
    Detects Claude Code approval patterns in OCR text

    Strict matching rules:
    1. Must contain "do you want to proceed"
    2. Must have "1. yes" (option 1 starts with yes)
    3. Must have "2. yes" (option 2 starts with yes)
    4. Optionally "3. no" (3-option dialog)
    """

    def __init__(self, patterns: ApprovalPatterns):
        self.patterns = patterns

    def check_approval_pattern(self, text: str) -> MatchResult:
        """
        Check if text contains Claude Code approval pattern

        Strict rules:
        - "do you want to proceed" must exist
        - "1. yes" must exist
        - "2. yes" must exist

        Args:
            text: OCR extracted text

        Returns:
            MatchResult with detection details
        """
        if not text:
            return MatchResult(is_match=False, debug_info="Empty text")

        text_lower = text.lower()
        text_normalized = ' '.join(text_lower.split())

        # Check 1: Question pattern (required)
        has_question = self.patterns.question_pattern in text_normalized
        if not has_question:
            return MatchResult(
                is_match=False,
                matched_question=False,
                debug_info=f"Missing question: '{self.patterns.question_pattern}'"
            )

        # Check 2: Option 1 must be "yes" (required)
        has_option_1_yes = self._check_option_pattern(text_lower, self.patterns.option_1_alternatives)
        if not has_option_1_yes:
            return MatchResult(
                is_match=False,
                matched_question=True,
                has_option_1_yes=False,
                debug_info="Missing '1. yes' option"
            )

        # Check 3: Option 2 must be "yes" (required)
        has_option_2_yes = self._check_option_pattern(text_lower, self.patterns.option_2_alternatives)
        if not has_option_2_yes:
            return MatchResult(
                is_match=False,
                matched_question=True,
                has_option_1_yes=True,
                has_option_2_yes=False,
                debug_info="Missing '2. yes' option"
            )

        # Check 4: Option 3 "no" (optional - determines 2 vs 3 option dialog)
        has_option_3_no = self._check_option_pattern(text_lower, self.patterns.option_3_alternatives)

        # All required conditions met!
        return MatchResult(
            is_match=True,
            matched_question=True,
            has_option_1_yes=True,
            has_option_2_yes=True,
            has_option_3_no=has_option_3_no,
            debug_info="Claude Code approval dialog detected"
        )

    def _check_option_pattern(self, text: str, patterns: list) -> bool:
        """
        Check if any of the option patterns exist in text

        Args:
            text: Lowercase text to search
            patterns: List of patterns to check

        Returns:
            True if any pattern found
        """
        for pattern in patterns:
            if pattern in text:
                return True
        return False

    def determine_response_key(self, text: str) -> str:
        """
        Determine which key to press based on options

        Logic:
        - 3 options (has "3. no"): Select '2' (yes, and don't ask again)
        - 2 options (no "3. no"): Select '1' (yes)

        Args:
            text: OCR extracted text

        Returns:
            '1' or '2' depending on the options
        """
        if not text:
            return '1'

        text_lower = text.lower()

        # Check if 3-option dialog
        has_option_3 = self._check_option_pattern(text_lower, self.patterns.option_3_alternatives)

        if has_option_3:
            # 3 options: select 2 (yes, and don't ask again)
            print("[DEBUG] 3-option dialog -> selecting '2'")
            return '2'
        else:
            # 2 options: select 1 (yes)
            print("[DEBUG] 2-option dialog -> selecting '1'")
            return '1'

    def get_pattern_summary(self) -> str:
        """Get summary of current patterns for debugging"""
        return f"""
Strict Pattern Matching Rules:
  Question: "{self.patterns.question_pattern}"
  Option 1: {self.patterns.option_1_alternatives}
  Option 2: {self.patterns.option_2_alternatives}
  Option 3: {self.patterns.option_3_alternatives}

Logic:
  - 3 options (1=yes, 2=yes, 3=no) -> press '2'
  - 2 options (1=yes, 2=yes) -> press '1'
"""
