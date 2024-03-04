from dataclasses import dataclass
from typing import Callable, Any

import pytest


@dataclass
class Pointer:
    target: Callable[..., Any]
    full_name: str


def resolve_target_pointer(target: Callable[..., Any]) -> Pointer:

    # NOTE: currently only supports functions
    return Pointer(
        target=target,
        full_name=f"{target.__module__}.{target.__qualname__}",
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
