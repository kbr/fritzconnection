"""
Running functional tests against a router - if the router is present.
"""

import pytest
import requests

from ..core.fritzconnection import (
    FritzConnection,
)
from ..lib.fritzhomeauto import FritzHomeAutomation
from ..lib.fritzhosts import FritzHosts
from ..lib.fritzphonebook import FritzPhonebook
from ..lib.fritzstatus import FritzStatus
from ..lib.fritzwlan import FritzWLAN


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
    # on success the modelname should be a string:
    assert isinstance(fc.modelname, str)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize("use_tls", [False, True])
def test_soap_access(use_tls):
    """
    Test whether a soap access returns successful. The Service
    'DeviceInfo1' with the action 'GetInfo' should be provided by all
    router models – including repeaters - and provides access to the
    model name.
    """
    fc = FritzConnection(timeout=TIMEOUT, use_tls=use_tls)
    info = fc.call_action('DeviceInfo1', 'GetInfo')
    # on success the modelname should be a string:
    assert isinstance(info['NewModelName'], str)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize(
    "cls, use_tls", [
        (FritzHomeAutomation, False),
        (FritzHomeAutomation, True),
        (FritzHosts, False),
        (FritzHosts, True),
        (FritzPhonebook, False),
        (FritzPhonebook, True),
        (FritzStatus, False),
        (FritzStatus, True),
        (FritzWLAN, False),
        (FritzWLAN, True),
    ])
def test_library_api_arguments(cls, use_tls):
    obj = cls(timeout=TIMEOUT, use_tls=use_tls)
    # on success the modelname should be a string:
    assert isinstance(obj.modelname, str)
