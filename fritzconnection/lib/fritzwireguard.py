"""
Module to access WireGuard VPN connections via the FRITZ!Box Web UI API.

Only WireGuard-related endpoints are implemented here. Session handling and
REST-API calls reuse existing `fritzconnection` core functionality.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)

from __future__ import annotations

import logging
from typing import Any

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, Timeout

from fritzconnection.core.exceptions import FritzAuthorizationError

from .fritzbase import AbstractLibraryBase

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
API_VPN_CONNECTION = "generic/vpn/connection"

DEFAULT_TIMEOUT = 10
HEADERS_ACCEPT_JSON = {"Accept": "application/json"}
HEADERS_ACCEPT_ANY = {"Accept": "*/*"}


def _parse_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        return value.lower() in ("1", "true", "yes", "on")
    return bool(value)


def _normalize_connection(
    data: dict[str, Any],
) -> dict[str, Any] | None:
    """Normalize one WireGuard connection payload.

    For the currently supported Fritz!OS payload structure:
    - `active` is expected as the canonical active state
    - `uid` is expected inside the payload
    """
    if not isinstance(data, dict):
        return None

    uid = data.get(API_KEY_UID)
    if not uid:
        return None

    raw_active = data.get(API_KEY_ACTIVE)
    if raw_active is None:
        return None

    return {
        API_KEY_UID: str(uid),
        API_KEY_NAME: data.get(API_KEY_NAME, uid),
        API_KEY_ACTIVE: _parse_bool(raw_active),
        API_KEY_ACTIVATED: _parse_bool(data.get(API_KEY_ACTIVATED, False)),
        API_KEY_CONNECTED: _parse_bool(data.get(API_KEY_CONNECTED, False)),
    }


class FritzWireguard(AbstractLibraryBase):
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

        response = self._post_data_lua(API_PAGE_SHAREWIREGUARD)
        if response is None:
            return {}

        if not isinstance(response, dict):
            return {}
        data = response.get(API_KEY_DATA, response)
        if not isinstance(data, dict):
            return {}
        init_data = data.get(API_KEY_INIT, {})
        if not isinstance(init_data, dict):
            return {}
        connections = init_data.get(API_KEY_BOX_CONNECTIONS)

        if connections is None:
            return {}

        if isinstance(connections, dict):
            connection_payloads = connections.values()
        elif isinstance(connections, list):
            connection_payloads = connections
        else:
            return {}

        result: dict[str, dict[str, Any]] = {}
        for conn_data in connection_payloads:
            normalized = _normalize_connection(conn_data)
            if normalized is not None:
                result[normalized[API_KEY_UID]] = normalized
        return result

    def _vpn_connections_url(self) -> str:
        """URL for POST /data.lua."""
        return f"{self.fc.http_interface.router_url}/data.lua"

    def _post_data_lua(self, page: str) -> dict[str, Any] | None:
        """
        Calls `POST /data.lua` with `page=<...>` and returns parsed JSON.

        The endpoint is undocumented by AVM and might change between FRITZ!OS
        versions.
        """
        # Reuse core session handling (PBKDF2/MD5) and restore session if
        # needed. This lives in `fritzconnection.core.fritz_sid`.
        sid = self.fc.http_interface.get_sid()

        url = self._vpn_connections_url()
        headers = HEADERS_ACCEPT_JSON
        data = {"sid": sid, "page": page}

        try:
            response = self.fc.session.post(
                url, data=data, headers=headers, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            if not response.text.strip():
                return {}
            return response.json()
        except HTTPError as err:
            status_code = getattr(getattr(err, "response", None), "status_code", None)
            if status_code in (401, 403):
                raise FritzAuthorizationError(
                    f"Authorization failed for WireGuard listing (HTTP {status_code})"
                ) from err
            return None
        except (Timeout, RequestsConnectionError):
            return None
        except ValueError:
            # JSON parsing failed
            return None

    def toggle_vpn(self, connection_uid: str, enable: bool) -> bool:
        """
        Enable or disable the VPN connection with the given uid.

        Returns True if the active state matches `enable` after the call.
        """
        payload = {API_KEY_ACTIVATED: 1 if enable else 0}
        base = self.fc.http_interface.router_url
        extra_headers = {
            **HEADERS_ACCEPT_ANY,
            "Origin": base,
            "Referer": f"{base}/",
        }

        try:
            response = self.fc.call_rest_api(
                method="put",
                path=API_VPN_CONNECTION,
                uid=connection_uid,
                payload=payload,
                extra_headers=extra_headers,
            )
            if response.status_code in (401, 403):
                raise FritzAuthorizationError(
                    f"Authorization failed for WireGuard toggle (HTTP {response.status_code})"
                )
            if response.status_code != 200:
                return False
        except (Timeout, RequestsConnectionError, HTTPError):
            return False

        after = self.get_vpn_connections()
        if connection_uid not in after:
            return False
        return after[connection_uid][API_KEY_ACTIVE] == enable
