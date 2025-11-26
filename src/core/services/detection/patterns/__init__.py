"""
Pattern implementations for approval detection
Each pattern class follows OCP - new patterns can be added without modifying existing code
"""

from .base_pattern import BasePattern
from .question_pattern import QuestionPattern
from .action_pattern import ActionPattern
from .specific_pattern import SpecificPattern
from .option_pattern import OptionPattern

__all__ = [
    'BasePattern',
    'QuestionPattern',
    'ActionPattern',
    'SpecificPattern',
    'OptionPattern',
]
