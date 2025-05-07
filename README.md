# Checklist: Pytest Plugin to Show Unit Coverage

**Code** coverage tools like
[coverage.py](https://coverage.readthedocs.io/en/7.0.1/) show you the
instrumented code coverage of your tests, however it won't tell you if you've
written specific unit tests for each of your code's **units** (here unit meaning
function).

This package implements a mechanism for measuring and reporting unit coverage.
Instead of instrumenting your code you will need to mark tests with a
**pointer** to the unit that it is covering.

You can think of it like an automatic checklist maintainer for each
function in your codebase!

You can still use standard coverage tools for measuring actual branch
coverage.

This package works by collecting all of the pointed-to units during test
execution and persists these to the pytest cache (typically somewhere under
`.pytest_cache`). Then in subsequent runs you need only report the results.

## Usage

### Writing Tests

First you must write tests and associate ("point") them to "targets"
(i.e. functions or "units") in your source code.

For example if you have in your code this module `mypackage/widget.py`:

``` python
def foo(in):
    return in * 3
```

Then in your test suite you would write a unit test for this function
and mark it as relating to that unit, e.g. in `tests/test_widget.py`:

``` python

from mypackage.widget import foo

@pytest.mark.pointer(foo)
def test_foo():
    assert foo(3) == 9
```

This registers that you have a unit test that covers the function.

NOTE: that this just helps you keep track of having declared a test
for a function, not that it is actually tested properly.

---

You can also write pointers like this:

```python
@pytest.mark.pointer(target=foo)
```

You can ignore files by using the ignore glob patterns (see below).

You can ignore individual functions using comments like this:

``` python
def foo(in): # nochecklist:
    return in * 3
```

Only the `nochecklist:` token is required. You can add a comment on why
after it:

``` python
def foo(in): # nochecklist: not testable
    return in * 3
```

---

You can mark multiple tests as covering a function, e.g.:

```python

@pytest.mark.pointer(foo)
def test_foo_caseA():
    ...

@pytest.mark.pointer(foo)
def test_foo_caseB():
    ...

```

But currently you can't mark a single test as covering multiple
functions. Only the first mark in the decorator stack is used.

#### Tips

We recommend adding this to the top of your test file to make typing
less and to reduce visua clutter:

```python
import pytest

pointer = pytest.mark.pointer

@pointer(func)
def test_func():
    ...
```

### Invocation

This package adds a couple new options to the `pytest` CLI:

`--checklist-disabled` (default `False`)

When this is given will explicitly disable this plugin from all
collection and reporting. Useful for running non-unit tests. Automatic
disablement also occurs when neither `--checklist-collect` or
`--checklist-report` are provided.


`--checklist-collect=STR` (default `''`)

This explicitly indicates to collect target coverage results. An empty
string indicates not set. For the current directory specify `'.'`. If
empty, but `--checklist-report` is given results will be collected
using the default.


`--checklist-report` (default `False`)

When this flag is given a textual report will be given at the end of the test
run. Note that even if this is not given the coverage checks will still be run.

`--checklist-func-min-pass=INT` (default `1`)

This flag controls the number of target test pointer marks are needed to
get a "passing" target.

`--checklist-fail-under=FLOAT` (default `100.0`)

This flag controls the percentage of passing targets are needed for the entire
coverage check to pass. The percentage is always displayed even without
`--checklist-report`. If this test is failed then the test process exits with
code 1, which is useful for things like CI.

`--checklist-exclude=STR` (default `''`)

Specify files via a comma separated list of glob pattern relative to
the `--checklist-collect` root directory to ignore. For example
`utils.py,no_unit/*.py`. Because excluded files will not be collected,
targets in them will not show up in the ignored target section. If you
want to ignore specific targets use the inline comments.

`--checklist-report-ignored` (default `False`)

When this flag is given the final report will also display the ignored
targets that were collected but will not fail. Note that anything
excluded will not be in this collection.

`--checklist-report-passing` (default `False`)

When this flag is given the final report will display all the passing
targets. Otherwise, only the failing target lines will be shown.


#### Example

Here is an example from this project (at a past point) source code
under the `src` folder, requiring 1 pointer test per collected unit in
the code, for all functions.

```
pytest --color=yes --verbose --import-mode=importlib --capture=no --tb=native --test-data=test_data --checklist-collect src/pytest_checklist --checklist-report --checklist-func-min-pass=1 --checklist-fail-under=100
========================================== test session starts ==========================================
platform linux -- Python 3.9.18, pytest-8.0.2, pluggy-1.4.0 -- /home/user/pytest-checklist/.hatch/pytest-checklist/bin/python
cachedir: .pytest_cache
rootdir: /home/user/pytest-checklist
configfile: pytest.ini
plugins: checklist-0.3.2
collected 6 items

tests/test_app.py::test_resolve_ignore_patterns PASSED
tests/test_app.py::test_is_passing PASSED
tests/test_collector.py::test_detect_files PASSED
tests/test_collector.py::test_resolve_fq_modules PASSED
tests/test_collector.py::test_resolve_fq_targets PASSED
tests/test_data.py::test_data_dir PASSED

----------------------
Checklist unit coverage
========================================
                                                                                  
                                                                                  
                                                                                  
            List of functions in project and the number of tests for them
                                                                                  
                                                                                  
    1 ··· pytest_checklist.app.is_passing                                          
    1 ··· pytest_checklist.app.resolve_ignore_patterns                             
    0 ··· pytest_checklist.collector.Target.fq_name                                
    0 ··· pytest_checklist.collector.MethodQualNamesCollector.visit_FunctionDef    
    0 ··· pytest_checklist.collector.resolve_fq_targets                            
    1 ··· pytest_checklist.collector.detect_files                                  
    0 ··· pytest_checklist.collector.MethodQualNamesCollector.__init__             
    0 ··· pytest_checklist.collector.collect_case_passes                           
    1 ··· pytest_checklist.collector.resolve_fq_modules                            
    0 ··· pytest_checklist.pointer.resolve_target_pointer                          
    0 ··· pytest_checklist.pointer.resolve_pointer_mark_target                     
    0 ··· pytest_checklist.report.make_report                                      
                                                                                  
                                                                                  
                                                                                  
Checklist unit coverage failed. Target was 100.0, achieved 33.33333333333333.

END Checklist unit coverage
========================================
```

## Installation

``` shell
pip install pytest-checklist
```

## Limitations

`pytest-checklist` does not work with `pytest-xdist` currently.

## Contributing

You must install [hatch](https://hatch.pypa.io/latest/).

### Install Hooks

Uses the [lefthook](https://github.com/evilmartians/lefthook) hook
runner.

You will need to run this once to have hooks run on git pre-commit:

```sh
lefthook install
```
### Python Bootstrapping

If you want you can bootstrap python installations with Hatch:

```sh
hatch python install --private 3.12
```

Be sure to check the documentation to make sure your site
configuration of Hatch makes sense.

If you don't do this you will be responsible for installing a version
of python for development declared in the environment.

### Testing, linting, etc.


You can just run all QA with:

```sh
lefthook run pre-commit
```

Or individually:

```sh
hatch run format_check
hatch run lint
hatch run typecheck
```

You can run the other tasks manually:

```sh
hatch run format
hatch run test
```

### Building

```sh
hatch build
```
