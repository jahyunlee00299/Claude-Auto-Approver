"""Hidden tests for the option-selection episode (authored for the replay, NOT in the upstream history).

They state the behaviour the three historical commits introduced: pick the best approval option
by its text, never a "No"/"tell Claude"/"exit" option, never '3'.
"""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ocr_auto_approver import OCRAutoApprover  # noqa: E402


def key(text):
    return OCRAutoApprover.determine_response_key(None, text)


def test_empty_text_defaults_to_one():
    assert key("") == "1"
    assert key(None) == "1"


def test_plain_yes_no_picks_yes():
    assert key("Do you want to proceed?\n 1. Yes\n 2. No\n") == "1"


def test_session_wide_allow_is_preferred_over_plain_yes():
    text = ("Do you want to create foo.py?\n 1. Yes\n"
            " 2. Yes, allow all edits during this session (shift+tab)\n"
            " 3. No, and tell Claude what to do differently (esc)\n")
    assert key(text) == "2"


def test_dont_ask_again_is_preferred():
    text = "Run command?\n 1. Yes\n 2. Yes, and don't ask again for this command\n 3. No\n"
    assert key(text) == "2"


def test_trust_dialog_never_selects_exit():
    text = ("Quick safety check: Is this a project you created or one you trust?\n"
            " 1. Yes, I trust this folder\n 2. No, exit\n")
    assert key(text) == "1"


def test_exit_option_never_chosen_even_when_listed_first():
    text = "Quick safety check\n 1. No, exit\n 2. Yes, I trust this folder\n"
    assert key(text) == "2"


def test_never_returns_option_three():
    text = " 1. Type here to tell Claude what to do\n 2. No\n 3. Yes, proceed\n"
    assert key(text) in ("1", "2")


@pytest.mark.parametrize("text", [
    "1. Yes\n2. No\n3. Type here to tell Claude differently\n",
    "> 1) Yes\n  2) No, exit\n",
    "garbled ocr 1 Yes 2 No",
])
def test_result_is_always_a_valid_key(text):
    assert key(text) in ("1", "2")


# --- regression tests added by the improve unit (proposals 1 and 2) ---

def test_file_name_with_digit_in_question_is_not_an_option():
    text = ("Do you want to create file2.py?\n 1. Yes\n"
            " 2. Yes, allow all edits during this session (shift+tab)\n 3. No\n")
    assert key(text) == "2"


def test_option_text_starting_with_no_prefix_word_is_not_a_refusal():
    text = " 1. Proceed\n 2. Nothing more to ask, approve and allow\n"
    assert key(text) == "2"


def test_arrow_marker_before_option_number_still_parses():
    text = "Run it?\n \u203a 1. No, exit\n   2. Yes, I trust this folder\n"
    assert key(text) == "2"
