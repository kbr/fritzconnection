"""
Running functional tests against a router - if the router is present.
"""

import pytest
import requests

from ..core.fritzconnection import (
    FritzConnection,
)


TIMEOUT = 2.0  # give older models some time
NO_ROUTER = 'no router present'


def _no_router_present():
    try:
        requests.get('http://169.254.1.1/', timeout=TIMEOUT)
    except requests.ConnectionError:
        return True
    return False


no_router_present = _no_router_present()


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
def test_access_model_name():
    """
    Check whether description files are accessible.
    In this case there is some modelname available (a string).
    """
    fc = FritzConnection(timeout=TIMEOUT)
    assert isinstance(fc.modelname, str)
