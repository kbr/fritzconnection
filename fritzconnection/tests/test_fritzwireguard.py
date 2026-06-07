"""Tests for FritzWireguard module."""

from unittest.mock import MagicMock, patch

from fritzconnection.lib.fritzwireguard import (
    FritzWireguard,
    API_KEY_ACTIVE,
    API_KEY_NAME,
    API_KEY_UID,
    API_KEY_ACTIVATED,
)
from fritzconnection.core.exceptions import FritzAuthorizationError


def _mock_fc() -> MagicMock:
    mock_fc = MagicMock()
    mock_fc.address = "https://192.168.178.1"
    mock_fc.port = 49443
    mock_fc.soaper.user = "admin"
    mock_fc.soaper.password = "password"
    mock_fc.call_action.return_value = {"NewPort": 443}
    mock_fc.session = MagicMock()
    mock_fc.session.auth = object()
    mock_fc.call_rest_api = MagicMock()
    mock_fc.http_interface = MagicMock()
    mock_fc.http_interface.get_sid.return_value = "sid123"
    mock_fc.http_interface.router_url = "https://192.168.178.1:443"
    return mock_fc


def test_module_constants():
    assert API_KEY_ACTIVE == "active"
    assert API_KEY_NAME == "name"
    assert API_KEY_UID == "uid"


def test_get_vpn_connections_empty():
    fw = FritzWireguard(fc=_mock_fc())
    with patch.object(fw, "_post_data_lua", return_value=None):
        assert fw.get_vpn_connections() == {}


def test_get_vpn_connections_with_list_data():
    fw = FritzWireguard(fc=_mock_fc())
    mock_response = {
        "data": {
            "init": {
                "boxConnections": [
                    {
                        "uid": "uid-office",
                        "name": "Office",
                        "active": True,
                        "activated": True,
                        "connected": True,
                    }
                ]
            }
        }
    }
    with patch.object(fw, "_post_data_lua", return_value=mock_response):
        connections = fw.get_vpn_connections()
        assert connections["uid-office"]["name"] == "Office"
        assert connections["uid-office"]["active"] is True


def test_get_vpn_connections_with_dict_data():
    fw = FritzWireguard(fc=_mock_fc())
    mock_response = {
        "init": {
            "boxConnections": {
                "wg-1": {
                    "uid": "wg-1",
                    "name": "Remote",
                    "activated": False,
                    "connected": "0",
                    "active": "1",
                }
            }
        }
    }
    with patch.object(fw, "_post_data_lua", return_value=mock_response):
        connections = fw.get_vpn_connections()
        assert connections["wg-1"]["active"] is True
        assert connections["wg-1"]["connected"] is False

def test_get_vpn_connections_malformed():
    fw = FritzWireguard(fc=_mock_fc())
    with patch.object(fw, "_post_data_lua", return_value={"invalid": "data"}):
        assert fw.get_vpn_connections() == {}


def test_toggle_vpn_success():
    fw = FritzWireguard(fc=_mock_fc())
    after = {
        "uid-office": {
            API_KEY_UID: "uid-office",
            API_KEY_NAME: "Office",
            API_KEY_ACTIVE: True,
        }
    }
    with patch.object(fw, "get_vpn_connections", return_value=after):
        fw.fc.call_rest_api.return_value.status_code = 200
        assert fw.toggle_vpn("uid-office", enable=True) is True
        assert fw.fc.call_rest_api.call_count == 1
        assert fw.fc.call_rest_api.call_args.kwargs["method"] == "put"
        assert fw.fc.call_rest_api.call_args.kwargs["path"] == "generic/vpn/connection"
        assert fw.fc.call_rest_api.call_args.kwargs["uid"] == "uid-office"
        assert fw.fc.call_rest_api.call_args.kwargs["payload"] == {"activated": 1}
        extra_headers = fw.fc.call_rest_api.call_args.kwargs["extra_headers"]
        assert extra_headers["Origin"] == "https://192.168.178.1:443"
        assert extra_headers["Referer"] == "https://192.168.178.1:443/"


def test_toggle_vpn_none_response():
    fw = FritzWireguard(fc=_mock_fc())
    fw.fc.call_rest_api.return_value.status_code = 401
    try:
        fw.toggle_vpn("uid-office", enable=False)
        assert False, "Expected FritzAuthorizationError"
    except FritzAuthorizationError:
        pass


def test_toggle_vpn_verify_mismatch():
    fw = FritzWireguard(fc=_mock_fc())
    after = {
        "uid-office": {
            API_KEY_UID: "uid-office",
            API_KEY_NAME: "Office",
            API_KEY_ACTIVE: False,
        }
    }
    with patch.object(fw, "get_vpn_connections", return_value=after):
        fw.fc.call_rest_api.return_value.status_code = 200
        assert fw.toggle_vpn("uid-office", enable=True) is False


def test_toggle_vpn_ignores_activated_field():
    fw = FritzWireguard(fc=_mock_fc())
    after = {
        "uid-office": {
            API_KEY_UID: "uid-office",
            API_KEY_NAME: "Office",
            API_KEY_ACTIVE: False,
            API_KEY_ACTIVATED: True,
        }
    }
    with patch.object(fw, "get_vpn_connections", return_value=after):
        fw.fc.call_rest_api.return_value.status_code = 200
        assert fw.toggle_vpn("uid-office", enable=True) is False
