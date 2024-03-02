"""Tools for generating reports"""

from textwrap import dedent
from dataclasses import dataclass

from rich.console import Console
from rich.padding import Padding

from pytest_pointers.utils import FuncResult


def make_report(func_results: list[FuncResult]) -> Padding:

    def report_line(func_result: FuncResult):

        if func_result.is_pass:
            color = "green"
        elif func_result.num_pointers > 0:
            color = "blue"
        else:
            color = "red"

        test_count_str = f"{func_result.num_pointers: <2}"
        return f"[{color}]{test_count_str:·<5}[/{color}] {func_result.name}"

    report_lines = "\n".join([report_line(func_result) for func_result in func_results])

    report = dedent(
        f"""
        [bold]List of functions in project and the number of tests for them[/bold]

        \n{report_lines}
        """
    )

    return Padding(report, (2, 4), expand=False)


def print_report(
        console: Console,
        func_results: list[FuncResult],
    report: bool = False,
) -> None:
    """Print the report.

    Args
        report: If true will print the whole report.

    """
    console.print("")
    console.print("")
    console.print("----------------------")
    console.print("Pointers unit coverage")
    console.print("========================================")

    if report:

        report = make_report(func_results)

        console.print(report)

    console.print("END Pointers unit coverage")
    console.print("========================================")


def print_failed_coverage(
        console: Console,
    percent_pass_threshold: float,
    percent_passes: float,
) -> None:

    console.print(
        f"[bold red]Pointers unit coverage failed. Target was {percent_pass_threshold}, achieved {percent_passes}.[/bold red]"
    )
