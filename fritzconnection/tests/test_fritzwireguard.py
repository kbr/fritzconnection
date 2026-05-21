"""Tests for FritzWireguard module."""

from unittest.mock import MagicMock, patch

from fritzconnection.lib.fritzwireguard import (
    FritzWireguard,
    API_KEY_ACTIVE,
    API_KEY_NAME,
    API_KEY_UID,
)
from fritzconnection.lib.fritzwebui import FritzWebUI


def _mock_fc() -> MagicMock:
    mock_fc = MagicMock()
    mock_fc.address = "https://192.168.178.1"
    mock_fc.port = 49443
    mock_fc.soaper.user = "admin"
    mock_fc.soaper.password = "password"
    mock_fc.call_action.return_value = {"NewPort": 443}
    return mock_fc


def test_module_constants():
    assert API_KEY_ACTIVE == "active"
    assert API_KEY_NAME == "name"
    assert API_KEY_UID == "uid"


def test_fritzwireguard_inherits_fritzwebui():
    fw = FritzWireguard(fc=_mock_fc())
    assert isinstance(fw, FritzWebUI)


def test_get_vpn_connections_empty():
    fw = FritzWireguard(fc=_mock_fc())
    with patch.object(fw, "get_page_data", return_value=None):
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
    with patch.object(fw, "get_page_data", return_value=mock_response):
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
                    "active": "1",
                    "activated": False,
                    "connected": "0",
                }
            }
        }
    }
    with patch.object(fw, "get_page_data", return_value=mock_response):
        connections = fw.get_vpn_connections()
        assert connections["wg-1"]["active"] is True
        assert connections["wg-1"]["connected"] is False


def test_get_vpn_connections_malformed():
    fw = FritzWireguard(fc=_mock_fc())
    with patch.object(fw, "get_page_data", return_value={"invalid": "data"}):
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
        with patch.object(fw, "_request", return_value={}) as mock_request:
            assert fw.toggle_vpn("uid-office", enable=True) is True
            mock_request.assert_called_once_with(
                "/api/v0/generic/vpn/connection/uid-office",
                method="PUT",
                json_body={"activated": 1},
            )


def test_toggle_vpn_none_response():
    fw = FritzWireguard(fc=_mock_fc())
    with patch.object(fw, "_request", return_value=None):
        assert fw.toggle_vpn("uid-office", enable=False) is False


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
        with patch.object(fw, "_request", return_value={}):
            assert fw.toggle_vpn("uid-office", enable=True) is False
