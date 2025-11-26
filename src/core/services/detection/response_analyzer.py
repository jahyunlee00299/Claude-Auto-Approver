"""
Response Analyzer (SRP: Single Responsibility)
Analyzes detected text to determine the appropriate response key
"""

import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class ResponseAnalysis:
    """Analysis result for response key determination"""
    recommended_key: str
    option_count: int
    option_1_keyword: str = ''
    option_2_keyword: str = ''
    option_3_keyword: str = ''
    reason: str = ''


class ResponseAnalyzer:
    """
    Analyzes text to determine which key to press

    Logic:
    - If 3 options (1, 2, 3): Select option 2 (usually "yes, and don't ask again")
    - If 2 options (1, 2): Select option 1 (safer, one-time approval)
    """

    def analyze(self, text: str) -> ResponseAnalysis:
        """
        Analyze text to determine response key

        Args:
            text: OCR detected text

        Returns:
            ResponseAnalysis with recommended key and details
        """
        if not text:
            return ResponseAnalysis(
                recommended_key='1',
                option_count=0,
                reason='No text provided, defaulting to option 1'
            )

        lines = text.split('\n')

        # Extract option keywords
        option_1_keyword = ''
        option_2_keyword = ''
        option_3_keyword = ''

        for line in lines:
            line_stripped = line.strip().lower()

            # Extract first word after option number
            if '1.' in line_stripped or '1)' in line_stripped:
                option_1_keyword = self._extract_keyword(line_stripped, '1')

            elif '2.' in line_stripped or '2)' in line_stripped:
                option_2_keyword = self._extract_keyword(line_stripped, '2')

            elif '3.' in line_stripped or '3)' in line_stripped:
                option_3_keyword = self._extract_keyword(line_stripped, '3')

        # Determine option count
        has_option_3 = bool(option_3_keyword) or self._has_option_marker(text, '3')

        if has_option_3:
            # 3 options detected -> Select option 2 (usually "yes, and don't ask again")
            return ResponseAnalysis(
                recommended_key='2',
                option_count=3,
                option_1_keyword=option_1_keyword,
                option_2_keyword=option_2_keyword,
                option_3_keyword=option_3_keyword,
                reason='3 options detected - selecting option 2 (persistent approval)'
            )
        else:
            # 2 options detected -> Select option 1 (safer, one-time approval)
            return ResponseAnalysis(
                recommended_key='1',
                option_count=2,
                option_1_keyword=option_1_keyword,
                option_2_keyword=option_2_keyword,
                reason='2 options detected - selecting option 1 (one-time approval)'
            )

    def _extract_keyword(self, line: str, option_num: str) -> str:
        """
        Extract first word after option number

        Args:
            line: Line of text (lowercased)
            option_num: Option number ('1', '2', or '3')

        Returns:
            First word after the option marker
        """
        # Find position of option marker
        markers = [f'{option_num}.', f'{option_num})']
        pos = -1

        for marker in markers:
            if marker in line:
                pos = line.index(marker) + len(marker)
                break

        if pos == -1:
            return ''

        # Get text after marker
        after_number = line[pos:].strip()
        if not after_number:
            return ''

        # Extract first word (up to comma, space, or end)
        first_word = after_number.split(',')[0].split()[0] if after_number.split() else ''
        return first_word

    def _has_option_marker(self, text: str, option_num: str) -> bool:
        """
        Check if text contains an option marker

        Args:
            text: Full text
            option_num: Option number to check

        Returns:
            True if option marker found
        """
        for line in text.split('\n'):
            line_lower = line.strip().lower()
            pattern = rf'(?:^|[^\d]){option_num}[.)]'
            if re.search(pattern, line_lower):
                return True
        return False
