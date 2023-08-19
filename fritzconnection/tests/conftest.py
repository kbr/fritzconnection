from pathlib import Path
import pytest


@pytest.fixture
def datadir():
    """
    Simple fixture for getting data files
    """
    here = Path(__file__).parent / "xml"
    return here


def pytest_configure(config):
    config.addinivalue_line("markers", "routertest: mark test accessing the router")
