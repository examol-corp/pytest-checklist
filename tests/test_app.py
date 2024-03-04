from pathlib import Path

import pytest

from pytest_checklist.app import resolve_exclude_patterns, is_passing, TargetReport
from pytest_checklist.collector import TargetResult, Module, Target


@pytest.mark.pointer(target=resolve_exclude_patterns)
def test_resolve_exclude_patterns():

    assert resolve_exclude_patterns("") == set()
    assert resolve_exclude_patterns("file/path/to.py") == {"file/path/to.py"}
    assert resolve_exclude_patterns("file/path/to.py,other/something.py") == {
        "file/path/to.py",
        "other/something.py",
    }


@pytest.mark.pointer(target=is_passing)
def test_is_passing():

    mod = Module(Path("nothing"), fq_module_name="nothing")

    assert is_passing(
        [
            TargetReport(
                TargetResult(
                    Target(mod, "something"),
                    1,
                ),
                True,
            ),
            TargetReport(
                TargetResult(
                    Target(mod, "other"),
                    1,
                ),
                True,
            ),
        ],
        100.0,
    )[1]

    assert not is_passing(
        [
            TargetReport(
                TargetResult(
                    Target(mod, "other"),
                    1,
                ),
                False,
            ),
        ],
        100.0,
    )[1]

    assert is_passing(
        [
            TargetReport(
                TargetResult(
                    Target(mod, "other"),
                    1,
                ),
                False,
            ),
        ],
        0.0,
    )[1]
