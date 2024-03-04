"""Stuff for dealing with configuration, inputs, etc."""

from dataclasses import dataclass

from pytest_checklist.collector import TargetResult


@dataclass
class TargetReport:

    result: TargetResult
    passes: bool


def resolve_exclude_patterns(exclude_str: str) -> set[str]:
    if len(exclude_str) == 0:
        return set()

    else:
        return set(exclude_str.split(","))


def is_passing(
    reports: list[TargetReport],
    percent_pass_threshold: float,
) -> tuple[float, bool]:

    num_targets = sum([1 for report in reports if not report.result.target.ignored])

    total_passes = sum([1 if report.passes else 0 for report in reports])

    if total_passes == num_targets:
        percent_passes = 100.0
    elif total_passes > 0:
        percent_passes = (total_passes / num_targets) * 100
    else:
        percent_passes = 0.0

    passes = percent_passes >= percent_pass_threshold

    return percent_passes, passes
