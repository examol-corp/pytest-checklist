"""Stuff for dealing with configuration, inputs, etc."""

from pathlib import Path

from pytest_pointers.utils import FuncResult


def resolve_ignore_paths(source_dir: Path, ignore_str: str) -> set[Path]:
    if len(ignore_str) == 0:
        ignore_paths = set()

    else:
        parts = ignore_str.split(",")

        # expand globs
        path_parts = []
        for part in parts:
            part_matches = list(source_dir.glob(part))

            if len(part_matches) == 0:
                raise ValueError(f"No matches for pattern: {part}")

            path_parts.extend(part_matches)

        ignore_paths = set((source_dir / Path(p)).resolve() for p in path_parts)

        for ignore_path in ignore_paths:

            if ignore_path.suffix != ".py":
                raise ValueError(
                    f"Ignored file path is not a Python file: {ignore_path}"
                )

            if not ignore_path.exists():
                raise ValueError(f"Ignored file path does not exist: {ignore_path}")

    return ignore_paths


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
