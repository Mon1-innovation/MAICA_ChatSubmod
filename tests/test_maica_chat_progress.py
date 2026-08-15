import sys
from pathlib import Path

import pytest


PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "game" / "python-packages"
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

import maica_chat_progress


@pytest.mark.parametrize("return_code", ("canceled", "mtrigger_triggering"))
def test_normal_chat_exit_counts_as_success_even_without_a_message(return_code):
    assert maica_chat_progress.is_successful_chat_result(return_code)
    assert maica_chat_progress.next_successful_chat_count(3, return_code) == 4


@pytest.mark.parametrize("return_code", ("disconnected", None, "unexpected"))
def test_error_or_unknown_chat_exit_does_not_count(return_code):
    assert not maica_chat_progress.is_successful_chat_result(return_code)
    assert maica_chat_progress.next_successful_chat_count(3, return_code) == 3


def test_successful_chat_count_is_never_negative():
    assert maica_chat_progress.next_successful_chat_count(-4, "disconnected") == 0
    assert maica_chat_progress.next_successful_chat_count(-4, "canceled") == 1
