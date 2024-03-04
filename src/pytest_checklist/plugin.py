from pathlib import Path
import sys
import itertools as it

import pytest
from rich.console import Console

from pytest_checklist.pointer import resolve_pointer_mark_target
from pytest_checklist.app import is_passing, resolve_ignore_patterns
from pytest_checklist.defaults import DEFAULT_MIN_NUM_POINTERS, DEFAULT_PASS_THRESHOLD
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
        "--checklist-func-min-pass",
        action="store",
        dest="checklist_func_min_pass",
        default=DEFAULT_MIN_NUM_POINTERS,
        type=int,
        help="Minimum number of pointer marks for a unit to pass.",
    )
    group.addoption(
        "--checklist-fail-under",
        action="store",
        dest="checklist_fail_under",
        default=0.0,
        type=float,
        help="Minimum percentage of units to pass (exit 0), if greater than exit 1.",
    )
    group.addoption(
        "--checklist-collect",
        dest="checklist_collect",
        default="src",
        help="Gather targets and tests for them",
    )
    group.addoption(
        "--checklist-ignore",
        dest="checklist_ignore",
        default="",
        help="Source files to ignore in collection, comma separated.",
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

    # parse the ignore paths
    ignore_patterns = resolve_ignore_patterns(session.config.option.checklist_ignore)

    # collect all the functions by scanning the source code

    # first collect all files to look in
    check_paths = detect_files(source_dir, list(ignore_patterns))

    check_modules = resolve_fq_modules(
        check_paths,
        [Path(p) for p in sys.path],
    )

    targets = resolve_fq_targets(check_modules)

    # collect the pass/fails for all the units
    func_results = collect_case_passes(
        target_pointers,
        it.chain(*targets.values()),
        session.config.option.checklist_func_min_pass,
    )

    # test whether the whole thing passed
    if session.config.option.checklist_fail_under is None:
        percent_pass_threshold = DEFAULT_PASS_THRESHOLD
    else:
        percent_pass_threshold = session.config.option.checklist_fail_under

    percent_passes, passes = is_passing(func_results, percent_pass_threshold)

    console = Console()

    console.print("")
    console.print("")
    console.print("----------------------")
    console.print("Checklist unit coverage")
    console.print("========================================")

    if session.config.option.checklist_report:
        report_padding = make_report(func_results)

        console.print(report_padding)

    if not passes:

        session.testsfailed = 1

        console.print(
            f"[bold red]Checklist unit coverage failed. Target was {percent_pass_threshold}, achieved {percent_passes}.[/bold red]"
        )
        console.print("")

    else:

        console.print(
            f"[bold green]Checklist unit coverage passed! Target was {percent_pass_threshold}, achieved {percent_passes}.[/bold green]"
        )
        console.print("")

    console.print("END Checklist unit coverage")
    console.print("========================================")
