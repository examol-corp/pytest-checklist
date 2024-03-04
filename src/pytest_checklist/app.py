"""Stuff for dealing with configuration, inputs, etc."""

from pytest_checklist.collector import FuncResult


def resolve_ignore_patterns(ignore_str: str) -> set[str]:
    if len(ignore_str) == 0:
        return set()

    else:
        return set(ignore_str.split(","))


def is_passing(
    results: list[FuncResult], percent_pass_threshold: float
) -> tuple[float, bool]:

    num_funcs = len(results)

    total_passes = sum([1 if res.is_pass else 0 for res in results])

    if total_passes == num_funcs:
        percent_passes = 100.0
    elif total_passes > 0:
        percent_passes = (total_passes / num_funcs) * 100
    else:
        percent_passes = 0.0

    passes = percent_passes >= percent_pass_threshold

    return percent_passes, passes
