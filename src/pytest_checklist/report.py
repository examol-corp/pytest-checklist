"""Tools for generating reports"""

from textwrap import dedent
from rich.padding import Padding

from pytest_checklist.app import TargetReport


def make_report(
    target_reports: list[TargetReport],
    show_ignored: bool = False,
    show_passing: bool = False,
) -> Padding:  # nochecklist: Just renders a display

    def report_line(target_report: TargetReport):

        # if it passes
        if target_report.passes:
            color = "green"
            test_message_str = "PASS"

        # doesn't pass but there are tests for it
        elif target_report.result.num_pointers > 0:
            color = "blue"
            test_message_str = "FAIL"

        # if its ignored and passing
        elif target_report.result.target.ignored and target_report.passes:
            color = "cyan"
            test_message_str = "IGNORE"

        elif target_report.result.target.ignored:
            color = "yellow"
            test_message_str = "IGNORE"

        else:
            color = "red"
            test_message_str = "FAIL"

        test_result_str = (
            f"{test_message_str: <7}{target_report.result.num_pointers: <2}"
        )

        return f"[{color}]{test_result_str:-<5}[/{color}] {target_report.result.target.fq_name()}"

    report_lines = "\n".join(
        [
            report_line(target_report)
            for target_report in target_reports
            if not (
                (not show_ignored and target_report.result.target.ignored)
                or (not show_passing and target_report.passes)
            )
        ]
    )

    if len(report_lines) > 0:
        report = dedent(
            f"""
            [bold]List of functions in project and the number of tests for them[/bold]

            \n{report_lines}
            """
        )
    else:
        report = dedent("[bold]All targets covered![/bold]")

    return Padding(report, (2, 4), expand=False)
