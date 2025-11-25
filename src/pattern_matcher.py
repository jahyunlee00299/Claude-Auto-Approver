"""
Pattern Matcher for approval detection - Strict Claude Code detection
SOLID: Single Responsibility - Only handles pattern matching logic
"""
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
    has_option_2_type: bool = False
    has_option_3_no: bool = False
    dialog_type: str = ""  # "3-option" or "2-option"
    debug_info: Optional[str] = None


class PatternMatcher:
    """
    Detects Claude Code approval patterns in OCR text

    Supports two dialog types:

    3-option dialog:
        Do you want to proceed?
        > 1. Yes
          2. Yes, and don't ask again...
          3. No, and tell Claude...
        -> Press '2'

    2-option dialog:
        Do you want to proceed?
        > 1. Yes
          2. Type here to tell Claude...
        -> Press '1'
    """

    def __init__(self, patterns: ApprovalPatterns):
        self.patterns = patterns

    def check_approval_pattern(self, text: str) -> MatchResult:
        """
        Check if text contains Claude Code approval pattern

        Rules:
        - "do you want to proceed" must exist
        - "1. yes" must exist
        - Either "2. yes" (3-option) or "2. type" (2-option) must exist

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
                debug_info=f"Missing: '{self.patterns.question_pattern}'"
            )

        # Check 2: Option 1 "yes" (required)
        has_option_1_yes = self._check_pattern(text_lower, self.patterns.option_1_alternatives)
        if not has_option_1_yes:
            return MatchResult(
                is_match=False,
                matched_question=True,
                has_option_1_yes=False,
                debug_info="Missing '1. yes'"
            )

        # Check 3: Option 2 - either "yes" or "type"
        has_option_2_yes = self._check_pattern(text_lower, self.patterns.option_2_yes_alternatives)
        has_option_2_type = self._check_pattern(text_lower, self.patterns.option_2_type_alternatives)

        if not has_option_2_yes and not has_option_2_type:
            return MatchResult(
                is_match=False,
                matched_question=True,
                has_option_1_yes=True,
                debug_info="Missing '2. yes' or '2. type'"
            )

        # Check 4: Option 3 "no" (determines dialog type)
        has_option_3_no = self._check_pattern(text_lower, self.patterns.option_3_alternatives)

        # Determine dialog type
        if has_option_3_no or has_option_2_yes:
            dialog_type = "3-option"
        else:
            dialog_type = "2-option"

        # All required conditions met!
        return MatchResult(
            is_match=True,
            matched_question=True,
            has_option_1_yes=True,
            has_option_2_yes=has_option_2_yes,
            has_option_2_type=has_option_2_type,
            has_option_3_no=has_option_3_no,
            dialog_type=dialog_type,
            debug_info=f"Claude Code {dialog_type} dialog detected"
        )

    def _check_pattern(self, text: str, patterns: list) -> bool:
        """Check if any pattern exists in text"""
        return any(p in text for p in patterns)

    def determine_response_key(self, text: str) -> str:
        """
        Determine which key to press

        Logic:
        - 3-option (has "2. yes" or "3. no"): Press '2' (yes, and don't ask again)
        - 2-option (has "2. type"): Press '1' (yes)

        Args:
            text: OCR extracted text

        Returns:
            '1' or '2'
        """
        if not text:
            return '1'

        text_lower = text.lower()

        # Check dialog type
        has_option_2_yes = self._check_pattern(text_lower, self.patterns.option_2_yes_alternatives)
        has_option_3_no = self._check_pattern(text_lower, self.patterns.option_3_alternatives)

        if has_option_2_yes or has_option_3_no:
            # 3-option: select 2 (yes, and don't ask again)
            print("[DEBUG] 3-option dialog -> pressing '2'")
            return '2'
        else:
            # 2-option: select 1 (yes)
            print("[DEBUG] 2-option dialog -> pressing '1'")
            return '1'

    def get_pattern_summary(self) -> str:
        """Get summary of patterns for debugging"""
        return f"""
Claude Code Dialog Detection:

3-option dialog:
  Do you want to proceed?
  > 1. Yes
    2. Yes, and don't ask again...
    3. No, and tell Claude...
  -> Press '2'

2-option dialog:
  Do you want to proceed?
  > 1. Yes
    2. Type here to tell Claude...
  -> Press '1'

Patterns:
  Question: "{self.patterns.question_pattern}"
  Option 1: {self.patterns.option_1_alternatives}
  Option 2 (yes): {self.patterns.option_2_yes_alternatives}
  Option 2 (type): {self.patterns.option_2_type_alternatives}
  Option 3: {self.patterns.option_3_alternatives}
"""
