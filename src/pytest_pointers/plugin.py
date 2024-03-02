from pathlib import Path

import pytest
from rich.console import Console

from pytest_pointers.app import is_passing, resolve_ignore_paths
from pytest_pointers.defaults import DEFAULT_MIN_NUM_POINTERS, DEFAULT_PASS_THRESHOLD
from pytest_pointers.utils import FuncFinder, FuncResult, 
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
    if (
        not request.config.option.pointers_collect
        and not request.config.option.pointers_report
    ):
        return

    pointers = request.config.cache.get(CACHE_TARGETS, {})
    marker = request.node.get_closest_marker("pointer")
    if marker:
        target_full_name = None
        if "target" in marker.kwargs:
            # support for regular pointers
            # @pytest.mark.pointer(target=Some.for_test)
            target = marker.kwargs.get("target", None)
            target_full_name = f"{target.__module__}.{target.__qualname__}"
        elif len(marker.args) == 2:
            # support for property pointers
            # @pytest.mark.pointer(Some, 'for_test')
            target_parent, target_member = marker.args
            target_full_name = f"{target_parent.__module__}.{target_parent.__qualname__}.{target_member}"

        if target_full_name not in pointers:
            pointers[target_full_name] = []

        pointers[target_full_name].append(request.node.nodeid)
        request.config.cache.set(CACHE_TARGETS, pointers)


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
    ignore_paths = resolve_ignore_paths(session.config.option.pointers_ignore)

    # collect all the functions by scanning the source code
    funcs = FuncFinder(
        source_dir,
        ignore_paths=ignore_paths,
    )

    # collect the pass/fails for all the units

    func_results = []
    for func in funcs:
        test_count = len(pointers.get(func, []))

        is_pass = False

        if test_count >= session.config.option.pointers_func_min_pass:
            is_pass = True
        else:
            is_pass = False

        func_results.append(
            FuncResult(
                name=func,
                num_pointers=test_count,
                is_pass=is_pass,
            )
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
