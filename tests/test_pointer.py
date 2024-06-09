import pytest

from pytest_checklist.pointer import (Pointer, resolve_pointer_mark_target,
                                      resolve_target_pointer)

pointer = pytest.mark.pointer


def func_target():
    pass


class PropertyTarget:
    @property
    def property_target(self):
        pass


@pointer(target=resolve_target_pointer)
def test_resolve_target_pointer():

    assert resolve_target_pointer(func_target) == Pointer(
        func_target,
        "tests.test_pointer.func_target",
    )

    assert resolve_target_pointer(PropertyTarget.property_target) == Pointer(
        PropertyTarget.property_target,
        "tests.test_pointer.PropertyTarget.property_target",
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
