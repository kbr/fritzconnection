from pathlib import Path
import pytest


@pytest.fixture
def datadir():
    """
    Simple fixture for getting data files
    """
    here = Path(__file__).parent/'xml'
    return here



# -- skip slow running tests:
# usage:
#
#     @pytest.mark.slow
#     def slow_running_function():
#         pass
#
# https://stackoverflow.com/questions/47559524/pytest-how-to-skip-tests-unless-you-declare-an-option-flag
def pytest_addoption(parser, *_):
    parser.addoption(
        "--include-router",
        action="store_true",
        default=False,
        help="run tests accessing the router (slow!)"
    )


# def pytest_configure(config):
#     config.addinivalue_line("markers", "slow: mark test as slow to run")
#
#
# def pytest_collection_modifyitems(config, items):
#     if config.getoption("--runslow"):
#         # --runslow given in cli: do not skip slow tests
#         return
#     skip_slow = pytest.mark.skip(reason="need --runslow option to run")
#     for item in items:
#         if "slow" in item.keywords:
#             item.add_marker(skip_slow)

# -- end skip slow running tests
