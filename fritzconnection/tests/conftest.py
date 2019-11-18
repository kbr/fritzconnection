from pathlib import Path
import pytest


@pytest.fixture
def datadir():
    """
    Simple fixture for getting data files
    """
    here = Path(__file__).parent/'xml'
    return here
