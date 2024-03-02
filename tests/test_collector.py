import pytest

from pytest_pointers.collector import (
    resolve_fq_modules,
    detect_files,
    resolve_fq_targets,
)


@pytest.mark.pointer(target=detect_files)
def test_detect_files(test_data_dir):
    assert len(detect_files(test_data_dir / "detect_files")) == 2


@pytest.mark.pointer(target=resolve_fq_modules)
def test_resolve_fq_modules(test_data_dir):

    expected_module_fqs = [
        "mymodule.thing",
        "mymodule.other",
    ]

    search_dir = test_data_dir / "resolve_fq_modules"
    modpath = search_dir / "mymodule"
    submod_paths = [
        modpath / "thing.py",
        modpath / "other.py",
    ]

    fq_modnames = [
        module.fq_module_name
        for module in resolve_fq_modules(
            submod_paths,
            [search_dir],
        )
    ]

    assert fq_modnames == expected_module_fqs


# @pytest.mark.pointer(resolve_fq_targets)
def test_resolve_fq_targets(test_data_dir):

    expected_func_fqs = [
        # basics
        "mymodule.thing.foo",
        "mymodule.thing.bar",
        "mymodule.other.quick",
        "mymodule.other.fox",
        # some more challenging things
    ]

    search_dir = test_data_dir / "resolve_fq_targets"
    modpath = search_dir / "mymodule"
    submod_paths = modpath.glob("**/*.py")

    modules = resolve_fq_modules(
        submod_paths,
        [search_dir],
    )

    # resolve all the targets
    targets = resolve_fq_targets(modules)

    # then for each case
    case_expected = {
        "mymodule.thing": {
            "mymodule.thing.foo",
            "mymodule.thing.bar",
        },
        "mymodule.other": {
            "mymodule.other.quick",
            "mymodule.other.fox",
        },
        "mymodule.cases.async_methods": {"mymodule.cases.async_methods.Some.for_test"},
        "mymodule.cases.decorators": {
            "mymodule.cases.decorators.some_decor",
            "mymodule.cases.decorators.Some.for_test",
        },
        "mymodule.cases.multiclass_same_method": {
            "mymodule.cases.multiclass_same_method.Some.__init__",
            "mymodule.cases.multiclass_same_method.Some.for_test",
            "mymodule.cases.multiclass_same_method.Another.__init__",
            "mymodule.cases.multiclass_same_method.Another.for_test",
        },
        "mymodule.cases.multi_methods": {
            "mymodule.cases.multi_methods.Some.__init__",
            "mymodule.cases.multi_methods.Some.for_test",
        },
        # NOTE: should not even be in here
        # "mymodule.cases.ignored" : set(),
    }

    for fq_module, expected in case_expected.items():

        found_modules = set(target.fq_name() for target in targets[fq_module])

        assert found_modules == expected
