# Pytest Plugin to Show Unit Coverage

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
def foo(in): # nopointer:
    return in * 3
```

Only the `nopointer:` token is required. You can add a comment on why
after it:

``` python
def foo(in): # nopointer: not testable
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

`--pointers-collect=STR` (default `src`)

This explicitly indicates to collect unit coverage results. If not specified,
but `--pointers-report` is given results will be collected using the default.

`--pointers-ignore=STR` (default `''`)

Specify files via a comma separated list of glob pattern relative to the
`--pointers-collect` root directory to ignore. For example
`utils.py,no_unit/*.py`.

`--pointers-report` (default `False`)

When this flag is given a textual report will be given at the end of the test
run. Note that even if this is not given the coverage checks will still be run.

`--pointers-func-min-pass=INT` (default `2`)

This flag controls the number of unit test pointer marks are needed to get a
"passing" unit. In the report units with 0 pointers are shown as red, passing
numbers are green, and anything in between is blue.

`--pointers-fail-under=FLOAT` (default `0.0`)

This flag controls the percentage of passing units are needed for the entire
coverage check to pass. The percentage is always displayed even without
`--pointers-report`. If this test is failed then the test process exits with
code 1, which is useful for things like CI.


#### Example

Here is an example from this project (at a past point) source code
under the `src` folder, requiring 1 pointer test per collected unit in
the code, for all functions.

```
pytest --color=yes --verbose --import-mode=importlib --capture=no --tb=native --test-data=test_data --pointers-collect src/pytest_pointers --pointers-report --pointers-func-min-pass=1 --pointers-fail-under=100
========================================== test session starts ==========================================
platform linux -- Python 3.9.18, pytest-8.0.2, pluggy-1.4.0 -- /home/user/pytest-pointers/.hatch/pytest-pointers/bin/python
cachedir: .pytest_cache
rootdir: /home/user/pytest-pointers
configfile: pytest.ini
plugins: pointers-0.3.2
collected 6 items

tests/test_app.py::test_resolve_ignore_patterns PASSED
tests/test_app.py::test_is_passing PASSED
tests/test_collector.py::test_detect_files PASSED
tests/test_collector.py::test_resolve_fq_modules PASSED
tests/test_collector.py::test_resolve_fq_targets PASSED
tests/test_data.py::test_data_dir PASSED

----------------------
Pointers unit coverage
========================================
                                                                                  
                                                                                  
                                                                                  
            List of functions in project and the number of tests for them
                                                                                  
                                                                                  
    1 ··· pytest_pointers.app.is_passing                                          
    1 ··· pytest_pointers.app.resolve_ignore_patterns                             
    0 ··· pytest_pointers.collector.Target.fq_name                                
    0 ··· pytest_pointers.collector.MethodQualNamesCollector.visit_FunctionDef    
    0 ··· pytest_pointers.collector.resolve_fq_targets                            
    1 ··· pytest_pointers.collector.detect_files                                  
    0 ··· pytest_pointers.collector.MethodQualNamesCollector.__init__             
    0 ··· pytest_pointers.collector.collect_case_passes                           
    1 ··· pytest_pointers.collector.resolve_fq_modules                            
    0 ··· pytest_pointers.pointer.resolve_target_pointer                          
    0 ··· pytest_pointers.pointer.resolve_pointer_mark_target                     
    0 ··· pytest_pointers.report.make_report                                      
                                                                                  
                                                                                  
                                                                                  
Pointers unit coverage failed. Target was 100.0, achieved 33.33333333333333.

END Pointers unit coverage
========================================
```

## Installation

Just install from this git repository:

``` shell
pip install git+https://github.com/examol-corp/pytest-pointers.git
```

## Contributing

You must install [hatch](https://hatch.pypa.io/latest/).

### Testing, linting, etc.

```
hatch run format_check
hatch run format
hatch run lint
hatch run typecheck
hatch run test
```

### Building

