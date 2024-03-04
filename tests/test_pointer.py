import pytest

from pytest_checklist.pointer import (
    resolve_pointer_mark_target,
    resolve_target_pointer,
    Pointer,
)

pointer = pytest.mark.pointer


def func_target():
    pass


@pointer(target=resolve_target_pointer)
def test_resolve_target_pointer():

    assert resolve_target_pointer(func_target) == Pointer(
        func_target,
        "tests.test_pointer.func_target",
    )


@pointer(target=resolve_pointer_mark_target)
def test_resolve_pointer_mark_target():

    # positional arg
    mark = pytest.Mark(
        "pointer",
        (func_target,),
        {},
    )

    assert resolve_pointer_mark_target(mark) == Pointer(
        func_target,
        "tests.test_pointer.func_target",
    )

    # keyword syntax

    mark = pytest.Mark(
        "pointer",
        (),
        {"target": func_target},
    )

    assert resolve_pointer_mark_target(mark) == Pointer(
        func_target,
        "tests.test_pointer.func_target",
    )
