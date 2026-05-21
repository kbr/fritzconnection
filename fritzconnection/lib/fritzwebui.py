"""
Module for Fritz!Box Web UI API access (undocumented endpoints).
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)

from __future__ import annotations

import hashlib
import logging
import re
import time
import xml.etree.ElementTree as ET
from http.client import HTTP_PORT
from typing import Any

from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import HTTPError, Timeout

from ..core.fritzconnection import FritzConnection
from .fritzbase import AbstractLibraryBase

_LOGGER = logging.getLogger(__name__)

API_LOGIN = "/login_sid.lua"
API_DATA = "/data.lua"
API_LOGIN_VERSION = "?version=2"
AUTH_HEADER_PREFIX = "AVM-SID "

DEFAULT_TIMEOUT = 10
HTTP_STATUS_FORBIDDEN = 403
INVALID_SID_VALUE = "0000000000000000"

LOGIN_TAG_CHALLENGE = "Challenge"
LOGIN_TAG_SID = "SID"
LOGIN_TAG_BLOCKTIME = "BlockTime"

LOGIN_FORM_USERNAME = "username"
LOGIN_FORM_RESPONSE = "response"


def _parse_challenge_from_login_xml(content: str) -> str | None:
    try:
        root = ET.fromstring(content)
        challenge = root.find(LOGIN_TAG_CHALLENGE)
        return challenge.text if challenge is not None else None
    except ET.ParseError:
        return None


def _parse_sid_from_login_response(content: str) -> str | None:
    try:
        root = ET.fromstring(content)
        sid = root.find(LOGIN_TAG_SID)
        if sid is not None and sid.text and sid.text != INVALID_SID_VALUE:
            return sid.text
    except ET.ParseError:
        pass
    match = re.search(r'sid["\']?\s*[=:]\s*["\']?([0-9a-fA-F]{16})', content)
    if match:
        return match.group(1)
    return None


def _parse_blocktime_from_login_xml(content: str) -> int | None:
    try:
        root = ET.fromstring(content)
        blocktime = root.find(LOGIN_TAG_BLOCKTIME)
        if blocktime is not None and blocktime.text:
            return int(blocktime.text)
    except (ET.ParseError, ValueError):
        return None
    return None


def _calculate_pbkdf2_response(challenge: str, password: str) -> str | None:
    """Same algorithm as FritzHttp._get_pbkdf2_hash."""
    parts = challenge.split("$")
    if len(parts) < 5 or parts[0] != "2":
        return None
    iter1 = int(parts[1])
    salt1_hex = parts[2]
    iter2 = int(parts[3])
    salt2_hex = parts[4]
    salt1 = bytes.fromhex(salt1_hex)
    salt2 = bytes.fromhex(salt2_hex)
    hash1 = hashlib.pbkdf2_hmac("sha256", password.encode(), salt1, iter1)
    hash2 = hashlib.pbkdf2_hmac("sha256", hash1, salt2, iter2)
    return f"{salt2_hex}${hash2.hex()}"


def _calculate_md5_response(challenge: str, password: str) -> str:
    response_raw = f"{challenge}-{password}".encode("utf-16le")
    return f"{challenge}-{hashlib.md5(response_raw).hexdigest()}"


class FritzWebUI(AbstractLibraryBase):
    """
    Base class for Fritz!Box Web UI API access.

    Optional argument `fc` is a FritzConnection instance. Further
    arguments are forwarded to FritzConnection.__init__() if `fc` is
    not given.

    WARNING: Web UI endpoints are undocumented by AVM and may change
    without notice when the router OS is updated.
    """

    def __init__(self, fc: FritzConnection | None = None, *args, **kwargs) -> None:
        super().__init__(fc, *args, **kwargs)
        self._sid: str | None = None

    @property
    def _web_ui_port(self) -> int:
        if self.fc.address.startswith("https"):
            data = self.fc.call_action("X_AVM-DE_RemoteAccess1", "GetInfo")
            return int(data["NewPort"])
        return HTTP_PORT

    @property
    def _base_url(self) -> str:
        return f"{self.fc.address}:{self._web_ui_port}"

    def _ensure_sid(self) -> str | None:
        if self._sid is not None:
            return self._sid

        username = self.fc.soaper.user
        password = self.fc.soaper.password
        if not password:
            return None

        sid = self._try_pbkdf2_login(username, password)
        if sid is None:
            sid = self._try_md5_login(username, password)
        if sid is not None:
            self._sid = sid
        return sid

    def _try_pbkdf2_login(self, username: str, password: str) -> str | None:
        login_url = f"{self._base_url}{API_LOGIN}{API_LOGIN_VERSION}"
        try:
            response = self.fc.session.get(login_url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            content = response.text
        except (RequestsConnectionError, HTTPError, Timeout):
            return None

        challenge = _parse_challenge_from_login_xml(content)
        if challenge is None or not challenge.startswith("2$"):
            return None

        blocktime = _parse_blocktime_from_login_xml(content)
        if blocktime and blocktime > 0:
            time.sleep(blocktime)

        response_hash = _calculate_pbkdf2_response(challenge, password)
        if response_hash is None:
            return None

        login_data = {
            LOGIN_FORM_USERNAME: username,
            LOGIN_FORM_RESPONSE: response_hash,
        }
        try:
            response = self.fc.session.post(
                login_url, data=login_data, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return _parse_sid_from_login_response(response.text)
        except (RequestsConnectionError, HTTPError, Timeout):
            return None

    def _try_md5_login(self, username: str, password: str) -> str | None:
        login_url = f"{self._base_url}{API_LOGIN}"
        try:
            response = self.fc.session.get(login_url, timeout=DEFAULT_TIMEOUT)
            response.raise_for_status()
            content = response.text
        except (RequestsConnectionError, HTTPError, Timeout):
            return None

        challenge = _parse_challenge_from_login_xml(content)
        if challenge is None:
            return None

        login_data = {
            LOGIN_FORM_USERNAME: username,
            LOGIN_FORM_RESPONSE: _calculate_md5_response(challenge, password),
        }
        try:
            response = self.fc.session.post(
                login_url, data=login_data, timeout=DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            return _parse_sid_from_login_response(response.text)
        except (RequestsConnectionError, HTTPError, Timeout):
            return None

    def _request(
        self,
        endpoint: str,
        data: dict[str, Any] | None = None,
        *,
        method: str = "POST",
        json_body: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        if not self._ensure_sid():
            return None

        url = f"{self._base_url}{endpoint}"
        headers = {"Accept": "application/json"}

        try:
            if method == "GET":
                params = dict(data or {})
                params["sid"] = self._sid
                response = self.fc.session.get(
                    url, params=params, headers=headers, timeout=DEFAULT_TIMEOUT
                )
            elif method == "PUT":
                headers["Content-Type"] = "application/json"
                if self._sid:
                    headers["Authorization"] = f"{AUTH_HEADER_PREFIX}{self._sid}"
                headers.setdefault("Origin", self.fc.address)
                headers.setdefault("Referer", f"{self.fc.address}/")
                response = self.fc.session.put(
                    url, headers=headers, json=json_body, timeout=DEFAULT_TIMEOUT
                )
            else:
                post_data = dict(data or {})
                post_data["sid"] = self._sid
                response = self.fc.session.post(
                    url, data=post_data, headers=headers, timeout=DEFAULT_TIMEOUT
                )

            response.raise_for_status()
            if not response.text.strip():
                return {}
            try:
                return response.json()
            except ValueError:
                return None
        except HTTPError as err:
            if err.response is not None and err.response.status_code == HTTP_STATUS_FORBIDDEN:
                self._sid = None
                if self._ensure_sid():
                    return self._request(endpoint, data, method=method, json_body=json_body)
            return None
        except (Timeout, RequestsConnectionError):
            return None

    def get_page_data(self, page: str) -> dict[str, Any] | None:
        return self._request(API_DATA, {"page": page})

    def invalidate_session(self) -> None:
        self._sid = None
