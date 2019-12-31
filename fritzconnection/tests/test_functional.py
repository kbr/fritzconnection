"""
Running functional tests against a router - if the router is present.
"""

import pytest
import requests

from ..core.exceptions import FritzConnectionException
from ..core.fritzconnection import FritzConnection
from ..lib.fritzcall import FritzCall
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


@pytest.fixture(scope="module")
def get_fc_instance():
    return FritzConnection(timeout=TIMEOUT)


@pytest.fixture(scope="module")
def get_fc_tls_instance():
    return FritzConnection(timeout=TIMEOUT, use_tls=True)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize("use_tls", [False, True])
def test_access_model_name(use_tls, get_fc_instance, get_fc_tls_instance):
    """
    Check whether description files are accessible.
    In this case there is some modelname available (a string).
    """
    if use_tls:
        fc = get_fc_instance
    else:
        fc = get_fc_tls_instance
    # on success the modelname should be a string:
    assert isinstance(fc.modelname, str)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize("use_tls", [False, True])
def test_soap_access(use_tls, get_fc_instance, get_fc_tls_instance):
    """
    Test whether a soap access returns successful. The Service
    'DeviceInfo1' with the action 'GetInfo' should be provided by all
    router models – including repeaters - and provides access to the
    model name.
    """
    if use_tls:
        fc = get_fc_instance
    else:
        fc = get_fc_tls_instance
    try:
        info = fc.call_action('DeviceInfo1', 'GetInfo')
    except FritzConnectionException:
        # will not work on devices requiring a password
        # to access a tr64 service.
        # fake success and skip
        assert True
    else:
        # on success the modelname should be a string:
        assert isinstance(info['NewModelName'], str)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize(
    "cls, use_tls", [
        (FritzCall, False),
        (FritzCall, True),
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


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize(
    "cls", [
        FritzCall,
        FritzHomeAutomation,
        FritzHosts,
        FritzPhonebook,
        FritzStatus,
        FritzWLAN
    ])
def test_init_cls_with_instance(cls, get_fc_instance):
    obj = cls(fc=get_fc_instance)
    assert isinstance(obj.modelname, str)


@pytest.mark.skipif(no_router_present, reason=NO_ROUTER)
@pytest.mark.parametrize(
    "cls", [
        FritzCall,
        FritzHomeAutomation,
        FritzHosts,
        FritzPhonebook,
        FritzStatus,
        FritzWLAN
    ])
def test_init_cls_with_tls_instance(cls, get_fc_tls_instance):
    obj = cls(fc=get_fc_tls_instance)
    assert isinstance(obj.modelname, str)
