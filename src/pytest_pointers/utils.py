import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Set
from collections.abc import Collection

import libcst as cst
from libcst.metadata import QualifiedNameProvider, ParentNodeProvider


class MethodQualNamesCollector(cst.CSTVisitor):
    METADATA_DEPENDENCIES = (QualifiedNameProvider, ParentNodeProvider)

    def __init__(self):
        self.found = []
        super().__init__()

    def visit_FunctionDef(self, node: cst.FunctionDef):
        header = getattr(node.body, "header", None)
        excluded = (
            header is not None
            and header.comment
            and header.comment.value.find("notest:") > -1
        )

        if not excluded:
            # TODO: Find better way to remove locals
            qual_names = self.get_metadata(QualifiedNameProvider, node)
            for qn in qual_names:
                from_local = qn.name.find("<locals>") > -1
                if not from_local:
                    self.found.append(qn.name)


@dataclass
class FuncFinder:
    start_dir: Path
    ignore_paths: Collection[Path] = field(default_factory=list)

    @classmethod
    def get_methods_qual_names(cls, node: cst.Module):
        collector = MethodQualNamesCollector()
        cst.MetadataWrapper(node).visit(collector)
        for method_name in collector.found:
            yield method_name

    def get_py_files(self) -> Set[Path]:

        py_files = set(
            [
                path
                for path in self.start_dir.glob("**/*.py")
                if path not in self.ignore_paths
            ]
        )

        for pattern in [".venv/**/*.py", "venv/**/*.py", "tests/**/*.py"]:
            py_files = py_files - set(self.start_dir.rglob(pattern))

        return py_files

    def __iter__(self):
        source_paths = [Path(p) for p in sys.path]

        py_files = self.get_py_files()

        for p in py_files:
            with open(p, "r") as f:
                tree = cst.parse_module(f.read())

            source = min(set(p.parents) & set(source_paths))
            abs_import = p.parts[len(source.parts) : -1] + (p.stem,)

            for fun_name in self.get_methods_qual_names(tree):
                yield ".".join(abs_import + (fun_name,))


@dataclass
class FuncResult:
    name: str
    num_pointers: int
    is_pass: bool


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
