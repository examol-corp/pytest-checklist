"""Tools for generating reports"""

from textwrap import dedent
from rich.padding import Padding

from pytest_pointers.collector import FuncResult


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
