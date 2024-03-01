from pathlib import Path

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--test-data",
        action="store",
        default="test_data",
    )


@pytest.fixture
def test_data_dir(request):

    test_data_path = Path(request.config.getoption("--test-data"))

    if not test_data_path.exists():

        raise ValueError(f"Test data path {test_data_path} does not exist.")

    elif not test_data_path.is_dir():
        raise ValueError(f"Test data path {test_data_path} is not a directory.")

    return test_data_path
