from typing import Union, Iterable
from dataclasses import dataclass
from pathlib import Path
from collections import defaultdict

import libcst as cst
from libcst.metadata import QualifiedNameProvider, ParentNodeProvider

from pytest_pointers.defaults import DEFAULT_NO_COVER_TOKEN


class MethodQualNamesCollector(cst.CSTVisitor):
    """Collector using the CST library visitor pattern."""

    METADATA_DEPENDENCIES = (QualifiedNameProvider, ParentNodeProvider)

    def __init__(self):  # nopointer:
        self.found = []
        super().__init__()

    def visit_FunctionDef(self, node: cst.FunctionDef):  # nopointer: DEBUG
        header = getattr(node.body, "header", None)
        excluded = (
            header is not None
            and header.comment
            and header.comment.value.find(DEFAULT_NO_COVER_TOKEN) > -1
        )

        if not excluded:
            # TODO: Find better way to remove locals
            qual_names = self.get_metadata(QualifiedNameProvider, node)
            for qn in qual_names:
                from_local = qn.name.find("<locals>") > -1
                if not from_local:
                    self.found.append(qn.name)


def detect_files(
    start_dir: Path,
    ignore_patterns: Union[list[str], None] = None,
) -> list[Path]:
    """Given the path and ignores return the set of files to parse."""

    # first identify all the paths to ignore
    ignore_paths: set[Path] = set()
    if ignore_patterns is not None:
        for pattern in ignore_patterns:
            ignore_paths |= set(start_dir.rglob(pattern))

    # then enumerate all the other paths, without the ignores.
    paths = set(
        [path for path in start_dir.glob("**/*.py") if path not in ignore_paths]
    )

    # return them in a sorted order so the output later on is stable
    return sorted(paths)


@dataclass(eq=True, frozen=True)
class Module:

    path: Path
    fq_module_name: str


@dataclass(eq=True, frozen=True)
class Target:

    module: Module
    name: str

    def fq_name(self) -> str:
        return f"{self.module.fq_module_name}.{self.name}"


def resolve_fq_modules(
    module_paths: list[Path],
    search_paths: list[Path],
) -> list[Module]:

    modules = []
    for module_path in module_paths:

        # first get the module that this file comes from
        source = min(set(module_path.parents) & set(search_paths))
        abs_import = module_path.parts[len(source.parts) : -1] + (module_path.stem,)

        fq_module_name = ".".join(abs_import)

        modules.append(Module(module_path, fq_module_name))

    return modules


def resolve_fq_targets(
    modules: list[Module],
) -> dict[str, set[Target]]:

    targets = defaultdict(set)

    for module in modules:

        # parse the module
        module_cst = cst.parse_module(module.path.read_text())

        # with the tree use the collector to retrieve the method names
        collector = MethodQualNamesCollector()
        cst.MetadataWrapper(module_cst).visit(collector)
        for method_name in collector.found:

            target = Target(
                module,
                method_name,
            )

            targets[module.fq_module_name].add(target)

    return dict(targets)


@dataclass
class FuncResult:
    name: str
    num_pointers: int
    is_pass: bool


def collect_case_passes(
    target_pointers: dict[str, set[str]],
    targets: Iterable[Target],
    num_min_pass: int,
) -> list[FuncResult]:

    func_results = []
    for target in targets:
        test_count: int = len(target_pointers.get(target.fq_name(), {}))

        is_pass = test_count >= num_min_pass

        func_results.append(
            FuncResult(
                name=target.fq_name(),
                num_pointers=test_count,
                is_pass=is_pass,
            )
        )

    return func_results
