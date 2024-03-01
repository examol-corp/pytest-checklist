"""Just test that the data is being loaded properly."""


def test_data_dir(test_data_dir):

    test_data_files = list(test_data_dir.iterdir())
    assert len(test_data_files) > 0

    print(test_data_files[0])
    print(test_data_files[0].read_text())
