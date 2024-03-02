from pathlib import Path

import pytest
from rich.console import Console

from pytest_pointers.pointer import resolve_pointer_mark_target
from pytest_pointers.app import is_passing, resolve_ignore_paths
from pytest_pointers.defaults import DEFAULT_MIN_NUM_POINTERS, DEFAULT_PASS_THRESHOLD
from pytest_pointers.utils import FuncFinder, FuncResult, collect_case_passes
from pytest_pointers.report import print_report, print_failed_coverage

CACHE_TARGETS = "pointers/targets"
CACHE_ALL_FUNC = "pointers/funcs"


def pytest_addoption(parser):
    group = parser.getgroup("pointers")
    group.addoption(
        "--pointers-report",
        action="store_true",
        dest="pointers_report",
        default=False,
        help="Show report in console",
    )
    group.addoption(
        "--pointers-func-min-pass",
        action="store",
        dest="pointers_func_min_pass",
        default=DEFAULT_MIN_NUM_POINTERS,
        type=int,
        help="Minimum number of pointer marks for a unit to pass.",
    )
    group.addoption(
        "--pointers-fail-under",
        action="store",
        dest="pointers_fail_under",
        default=0.0,
        type=float,
        help="Minimum percentage of units to pass (exit 0), if greater than exit 1.",
    )
    group.addoption(
        "--pointers-collect",
        dest="pointers_collect",
        default="src",
        help="Gather targets and tests for them",
    )
    group.addoption(
        "--pointers-ignore",
        dest="pointers_ignore",
        default="",
        help="Source files to ignore in collection, comma separated.",
    )


def pytest_configure(config):
    config.addinivalue_line("markers", "pointer(element): Define a tested element.")


def pytest_sessionstart(session: pytest.Session):
    if session.config.option.pointers_collect or session.config.option.pointers_report:

        if session.config.cache is not None:
            session.config.cache.set(CACHE_TARGETS, {})


@pytest.fixture(scope="function", autouse=True)
def _pointer_marker(request):
    """Fixture that is autoinjected to each test case.

    It will detect if there is a pointer marker and register this test
    case to the target.

    """

    
    if (
        not request.config.option.pointers_collect
        and not request.config.option.pointers_report
    ):
        return None


    # load the cached pointers, or create if not existing

    # this is a structure mapping a unique 'target' (the unit you want
    # to record coverage for) and the test cases that target it. Each
    # test case has a "pointer" to the target.
    target_pointers: dict[str, set[str]] = {
        target : set(pointers)
        for target, pointers
        in request.config.cache.get(CACHE_TARGETS, {}).items()
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
    request.config.cache.set(CACHE_TARGETS,
                             {
                                 target : list(pointers)
                                 for target, pointers
                                 in target_pointers.items()
                             })


@pytest.hookimpl(hookwrapper=True)
def pytest_runtestloop(session):

    # do the report here so we can give the exit code, in pytest_sessionfinish
    # you cannot alter the exit code

    # run the inner hook
    yield

    # after the runtestloop is finished we can generate the report etc.

    pointers = session.config.cache.get(CACHE_TARGETS, {})

    start_dir = Path(session.startdir)

    # the collect option can also tell where to start within the project,
    # otherwise it will collect a lot of wrong paths in virtualenvs etc.
    source_dir = start_dir / session.config.option.pointers_collect

    # parse the ignore paths
    ignore_paths = resolve_ignore_paths(source_dir, session.config.option.pointers_ignore)

    # collect all the functions by scanning the source code
    func_finder = FuncFinder(
        source_dir,
        ignore_paths=ignore_paths,
    )

    # collect the pass/fails for all the units
    func_results = collect_case_passes(
        pointers, func_finder, session.config.option.pointers_func_min_pass
    )

    # test whether the whole thing passed
    if session.config.option.pointers_fail_under is None:
        percent_pass_threshold = DEFAULT_PASS_THRESHOLD
    else:
        percent_pass_threshold = session.config.option.pointers_fail_under

    percent_passes, passes = is_passing(func_results, percent_pass_threshold)

    console = Console()

    if not passes:

        session.testsfailed = 1

        print_failed_coverage(console, percent_pass_threshold, percent_passes)

    print_report(
        console,
        func_results,
        report=session.config.option.pointers_report,
    )
