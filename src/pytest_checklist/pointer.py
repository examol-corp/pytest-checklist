from dataclasses import dataclass
from typing import Any, Callable

import pytest


@dataclass
class Pointer:
    target: Callable[..., Any] | property
    full_name: str


def resolve_target_pointer(target: Callable[..., Any]) -> Pointer:
    # NOTE: currently only supports functions and properties

    if isinstance(target, property):
        module = target.fget.__module__
        qualname = target.fget.__qualname__
    else:
        module = target.__module__
        qualname = target.__qualname__

    full_name = f"{module}.{qualname}"

    return Pointer(
        target=target,
        full_name=full_name,
    )


def resolve_pointer_mark_target(mark: pytest.Mark) -> Pointer:

    # support writing pointers in two ways:
    #
    # pointer(name_of_target)
    #
    # pointer(target=name_of_target)

    num_args = len(mark.args)
    if num_args == 1:

        target = mark.args[0]

        if "target" in mark.kwargs:
            raise ValueError("'target' already given as positional argument.")

    elif "target" in mark.kwargs:
        target = mark.kwargs["target"]

    else:
        raise ValueError("No positional or kwarg given for pointer target.")

    return resolve_target_pointer(target)
