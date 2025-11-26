"""
Detection Service implementations
"""

from .composite_pattern_detector import CompositePatternDetector
from .response_analyzer import ResponseAnalyzer
from .patterns import (
    QuestionPattern,
    ActionPattern,
    SpecificPattern,
    OptionPattern,
)

__all__ = [
    'CompositePatternDetector',
    'ResponseAnalyzer',
    'QuestionPattern',
    'ActionPattern',
    'SpecificPattern',
    'OptionPattern',
]
