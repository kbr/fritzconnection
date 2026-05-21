"""
Module to access WireGuard VPN connections via the Fritz!Box Web UI API.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)

from __future__ import annotations

import logging
from typing import Any

from .fritzwebui import FritzWebUI

_LOGGER = logging.getLogger(__name__)

API_KEY_DATA = "data"
API_KEY_INIT = "init"
API_KEY_BOX_CONNECTIONS = "boxConnections"
API_KEY_UID = "uid"
API_KEY_ACTIVE = "active"
API_KEY_ACTIVATED = "activated"
API_KEY_CONNECTED = "connected"
API_KEY_NAME = "name"

API_PAGE_SHAREWIREGUARD = "shareWireguard"
API_VPN_CONNECTION = "/api/v0/generic/vpn/connection/{uid}"


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("1", "true", "yes", "on")
    return bool(value)


def _normalize_connection(data: dict[str, Any]) -> dict[str, Any] | None:
    if not isinstance(data, dict):
        return None
    uid = data.get(API_KEY_UID)
    if not uid:
        return None
    return {
        API_KEY_UID: uid,
        API_KEY_NAME: data.get(API_KEY_NAME, uid),
        API_KEY_ACTIVE: _parse_bool(data.get(API_KEY_ACTIVE, False)),
        API_KEY_ACTIVATED: _parse_bool(data.get(API_KEY_ACTIVATED, False)),
        API_KEY_CONNECTED: _parse_bool(data.get(API_KEY_CONNECTED, False)),
    }


class FritzWireguard(FritzWebUI):
    """
    Class to list and toggle WireGuard VPN connections.

    All parameters are optional. If given, they have the following
    meaning: `fc` is an instance of FritzConnection, `address` the ip of
    the Fritz!Box, `port` the port to connect to, `user` the username,
    `password` the password, `timeout` a timeout as floating point number
    in seconds, `use_tls` a boolean indicating to use TLS (default False).
    """

    def get_vpn_connections(self) -> dict[str, dict[str, Any]]:
        """Return WireGuard VPN connections keyed by uid."""
        response = self.get_page_data(API_PAGE_SHAREWIREGUARD)
        if response is None:
            return {}

        try:
            data = response.get(API_KEY_DATA, response)
            init_data = data.get(API_KEY_INIT, {})
            connections = init_data.get(API_KEY_BOX_CONNECTIONS)
        except (AttributeError, TypeError):
            return {}

        if connections is None:
            return {}

        result: dict[str, dict[str, Any]] = {}
        if isinstance(connections, dict):
            for conn_data in connections.values():
                normalized = _normalize_connection(conn_data)
                if normalized is not None:
                    result[normalized[API_KEY_UID]] = normalized
        elif isinstance(connections, list):
            for conn in connections:
                normalized = _normalize_connection(conn)
                if normalized is not None:
                    result[normalized[API_KEY_UID]] = normalized
        return result

    def toggle_vpn(self, connection_uid: str, enable: bool) -> bool:
        """
        Enable or disable the VPN connection with the given uid.

        Returns True if the active state matches `enable` after the call.
        """
        if self._request(
            API_VPN_CONNECTION.format(uid=connection_uid),
            method="PUT",
            json_body={API_KEY_ACTIVATED: 1 if enable else 0},
        ) is None:
            return False

        after = self.get_vpn_connections()
        if connection_uid not in after:
            return False
        return after[connection_uid][API_KEY_ACTIVE] is enable
