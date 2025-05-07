# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- When neither `--checklist-collect` nor `--checklist-report` are
  given `pytest-checklist` is disabled.
- When the value for `--checklist-collect=''` (empty string) no
  collection will take place.
- The default for `--checklist-collect` is now an empty string.

### Added

- `--checklist-disabled` flag is supported. Which overrides any other
  option.

### Fixed

- Fixed internal bug for the module search path when not setting
  `--checklist-infer-search-module`.

## [0.3.5]

### Added

- `--checklist-infer-search-module` flag which enables proper
  resolution of the module from with the `--checklist-collect` is
  collecting from. The previous behavior was to pick the first
  matching path that happens to be in `sys.path` that contains the
  `--checklist-collect` path. If this match matches on e.g. the
  current directory but the module import path is supposed to be set
  by `PYTHONPATH` or from normal package resolution this can result in
  the module fully qualified names being prepended by prefixes that
  don't match the modules as referenced in the test suite via import.
  - Currently this flag is not turned on by default but will be in an
    upcoming MINOR release. In the next MAJOR release this behavior
    (and this flag) will be completely deprecated.
  - Emits a deprecation warning.

### Removed

- Support for Python < 3.10
