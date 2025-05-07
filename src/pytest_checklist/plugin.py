from pathlib import Path
import sys
import itertools as it

import pytest
from rich.console import Console

from pytest_checklist.pointer import resolve_pointer_mark_target
from pytest_checklist.app import is_passing, resolve_exclude_patterns, TargetReport
from pytest_checklist.defaults import (
    DEFAULT_MIN_NUM_POINTERS,
    DEFAULT_PASS_THRESHOLD,
    DEFAULT_COLLECT_PATH,
)
from pytest_checklist.collector import (
    collect_case_passes,
    detect_files,
    resolve_fq_modules,
    resolve_fq_targets,
)
from pytest_checklist.report import make_report

CACHE_TARGETS = "checklist/targets"
CACHE_ALL_FUNC = "checklist/funcs"


def pytest_addoption(parser) -> None:  # nochecklist:
    group = parser.getgroup("checklist")
    group.addoption(
        "--checklist-report",
        action="store_true",
        dest="checklist_report",
        default=False,
        help="Show report in console",
    )
    group.addoption(
        "--checklist-target-min-pass",
        action="store",
        dest="checklist_target_min_pass",
        default=DEFAULT_MIN_NUM_POINTERS,
        type=int,
        help=f"Minimum number of pointer marks for a unit to pass.\nDefault {DEFAULT_MIN_NUM_POINTERS}",
    )
    group.addoption(
        "--checklist-fail-under",
        action="store",
        dest="checklist_fail_under",
        default=DEFAULT_PASS_THRESHOLD,
        type=float,
        help=f"Minimum percentage of units to pass (exit 0), if greater than exit 1.\nDefault: {DEFAULT_PASS_THRESHOLD}",
    )
    group.addoption(
        "--checklist-collect",
        dest="checklist_collect",
        default=DEFAULT_COLLECT_PATH,
        help=f"Gather targets and tests for them. \nDefault: '{DEFAULT_COLLECT_PATH}'",
    )
    group.addoption(
        "--checklist-exclude",
        dest="checklist_exclude",
        default="",
        help="Source files to exclude from collection, comma separated. Excluded files will not be collected and cannot be reported as ignored.",
    )
    group.addoption(
        "--checklist-report-ignored",
        action="store_true",
        dest="checklist_report_ignored",
        default=False,
        help="Show ignored units in checklist report.\nDefault: ''",
    )
    group.addoption(
        "--checklist-report-passing",
        action="store_true",
        dest="checklist_report_passing",
        default=False,
        help="Show passing units in checklist report.",
    )


def pytest_configure(config) -> None:  # nochecklist:
    config.addinivalue_line("markers", "pointer(element): Define a tested element.")


def pytest_sessionstart(session: pytest.Session) -> None:  # nochecklist:
    if (
        session.config.option.checklist_collect
        or session.config.option.checklist_report
    ):

        if session.config.cache is not None:
            session.config.cache.set(CACHE_TARGETS, {})


@pytest.fixture(scope="function", autouse=True)
def _pointer_marker(request) -> None:  # nochecklist:
    """Fixture that is autoinjected to each test case.

    It will detect if there is a pointer marker and register this test
    case to the target.

    """

    if (
        not request.config.option.checklist_collect
        and not request.config.option.checklist_report
    ):
        return None

    # load the cached pointers, or create if not existing

    # this is a structure mapping a unique 'target' (the unit you want
    # to record coverage for) and the test cases that target it. Each
    # test case has a "pointer" to the target.
    target_pointers: dict[str, set[str]] = {
        target: set(pointers)
        for target, pointers in request.config.cache.get(CACHE_TARGETS, {}).items()
    }

    # for this test, grab the first marker which is a pointer
    maybe_mark = request.node.get_closest_marker("pointer")

    # if present we handle it
    if maybe_mark is not None:

        pointer = resolve_pointer_mark_target(maybe_mark)

        # if there is no pointers to this target registered already,
        # initialize a list to store them in
        if pointer.full_name not in target_pointers:
            target_pointers[pointer.full_name] = set()

        # then we add this "nodeid" which is the specific test case
        target_pointers[pointer.full_name].add(request.node.nodeid)

    # then save the updated pointers to the cache
    request.config.cache.set(
        CACHE_TARGETS,
        {target: list(pointers) for target, pointers in target_pointers.items()},
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(session) -> None:  # nochecklist:

    # do the report here so we can give the exit code, in pytest_sessionfinish
    # you cannot alter the exit code

    # run the inner hook
    yield

    # after the runtestloop is finished we can generate the report etc.

    target_pointers = session.config.cache.get(CACHE_TARGETS, {})

    start_dir = Path(session.startdir)

    # the collect option can also tell where to start within the project,
    # otherwise it will collect a lot of wrong paths in virtualenvs etc.
    source_dir = start_dir / session.config.option.checklist_collect

    # parse the exclude paths
    exclude_patterns = resolve_exclude_patterns(session.config.option.checklist_exclude)

    # collect all the functions by scanning the source code

    # first collect all files to look in
    check_paths, _ = detect_files(source_dir, list(exclude_patterns))

    check_modules = resolve_fq_modules(
        check_paths,
        [Path(p) for p in sys.path],
    )

    targets = resolve_fq_targets(check_modules)

    # collect the pass/fails for all the units
    target_results = collect_case_passes(
        target_pointers,
        it.chain(*targets.values()),
    )

    target_min_pass = session.config.option.checklist_target_min_pass
    fail_under = session.config.option.checklist_fail_under

    target_reports = []
    for result in target_results:

        target_reports.append(
            TargetReport(result, passes=result.num_pointers >= target_min_pass)
        )

    # test whether the whole thing passed
    percent_passes, passes = is_passing(target_reports, fail_under)

    console = Console()

    console.print("")
    console.print("")
    console.print("----------------------")
    console.print("Checklist unit coverage")
    console.print("========================================")

    console.print(f"Minimum number of pointers per target: {target_min_pass}")

    if session.config.option.checklist_report:

        report_padding = make_report(
            target_reports,
            show_ignored=session.config.option.checklist_report_ignored,
            show_passing=session.config.option.checklist_report_passing,
        )

        console.print(report_padding)

    if not passes:

        session.testsfailed = 1

        console.print(
            f"[bold red]Checklist unit coverage failed. Target was {fail_under}, achieved {percent_passes}.[/bold red]"
        )
        console.print("")

    else:

        console.print(
            f"[bold green]Checklist unit coverage passed! Target was {fail_under}, achieved {percent_passes}.[/bold green]"
        )
        console.print("")

    console.print("END Checklist unit coverage")
    console.print("========================================")
