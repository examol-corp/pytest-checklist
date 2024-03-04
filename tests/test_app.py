import pytest

from pytest_checklist.collector import FuncResult
from pytest_checklist.app import resolve_ignore_patterns, is_passing


@pytest.mark.pointer(target=resolve_ignore_patterns)
def test_resolve_ignore_patterns():
    pass


@pytest.mark.pointer(target=is_passing)
def test_is_passing():

    assert is_passing(
        [
            FuncResult(
                "something",
                1,
                True,
            ),
            FuncResult(
                "other",
                1,
                True,
            ),
        ],
        100.0,
    )[1]

    assert not is_passing(
        [
            FuncResult(
                "something",
                1,
                False,
            ),
        ],
        100.0,
    )[1]

    assert is_passing(
        [
            FuncResult(
                "something",
                1,
                False,
            ),
        ],
        0.0,
    )[1]
