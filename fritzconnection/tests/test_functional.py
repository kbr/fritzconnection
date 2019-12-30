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
@pytest.mark.parametrize("use_tls", [False, True])
def test_access_model_name(use_tls):
    """
    Check whether description files are accessible.
    In this case there is some modelname available (a string).
    """
    fc = FritzConnection(timeout=TIMEOUT, use_tls=use_tls)
    assert isinstance(fc.modelname, str)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize("use_tls", [False, True])
def test_soap_access(use_tls):
    """
    Test whether a soap access returns successful. The Service
    'DeviceInfo1' with the action 'GetInfo' should be provided by all
    router models – including repeaters.
    """
    fc = FritzConnection(timeout=TIMEOUT, use_tls=use_tls)
    info = fc.call_action('DeviceInfo1', 'GetInfo')
    # on success the modelname should be a string:
    assert isinstance(info['NewModelName'], str)
