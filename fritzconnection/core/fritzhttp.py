"""
fritzhttp.py

Access the AVM Fritz!Box AHA-HTTP-Inferface
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import hashlib
from http import HTTPStatus
from http.client import HTTP_PORT
from xml.etree import ElementTree as etree

from fritzconnection.core.exceptions import (
    FritzHttpInterfaceError,
    FritzAuthorizationError,
)


URL_LOGIN = "/login_sid.lua?version=2"
URL_HOMEAUTOSWITCH = "/webservices/homeautoswitch.lua"
PBKDF2_CHALLENGE_INDICATOR = "2$"


class FritzHttp:
    """
    Implementation for the AVM AHA-HTTP-Inferface.

    The current implementation does not handle a blocktime timeout so
    far. This is because the communication is based on a
    fritzconnection-session and the proper credentials are already
    handled there.

    There may be the side-effect that someone else messes up with the
    login of the human web-interface while this script is running. In
    this case the aha-interface login will not return a valid sid until
    blocktime runs out.
    """
    def __init__(self, fc):
        self.fc = fc  # the active fritzconnection instance
        self.sid = None

    @property
    def remote_port(self):
        """
        Provides the configurable https port for the aha-interface as int.
        """
        if self.fc.address.startswith("https"):
            data = self.fc.call_action("X_AVM-DE_RemoteAccess1", "GetInfo")
            return int(data["NewPort"])  # provide same type as HTTP_PORT
        return HTTP_PORT

    @property
    def login_url(self):
        """The login-url including protocol and configurable port."""
        return f"{self.fc.address}:{self.remote_port}{URL_LOGIN}"

    @property
    def homeauto_url(self):
        """The homeauto-url including protocol and configurable port."""
        return f"{self.fc.address}:{self.remote_port}{URL_HOMEAUTOSWITCH}"

    def execute(self, command=None, identifier=None, **kwargs):
        """
        Send the command and the optional identifier to the
        http-interface and returns a tuple with the content-type and the
        response-text as is. On error raises a FritzAuthorizationError
        if the error code was 403 otherwise raises a generic
        FritzConnectionException with the corresponding error-code.

        The `command` is a string like 'getswitchlist' or
        'getbasicdevicestats' according to the AVM AHA documentation.

        The `identifier` is a string, representing a device-ain.
        """
        payload = {"switchcmd": command, "ain": identifier}
        payload.update(kwargs)
        for sid in self._get_sid():
            payload['sid'] = sid
            with self.fc.session.get(
                self.homeauto_url, params=payload
            ) as response:
                if response.status_code == HTTPStatus.OK:
                    return response.headers.get('content-type'), response.text
        msg = f"Request failed: http error code '{response.status_code}'"
        if response.status_code == HTTPStatus.FORBIDDEN:
            # can happen if FritzConnection was initialized
            # without a password.
            raise FritzAuthorizationError(msg)
        # This can be from the 400 or 500 error-family.
        # Most often these errors are triggered by a malformed payload,
        # therefore include the payload in the message:
        msg = f"{msg}, payload: {payload}"
        raise FritzHttpInterfaceError(msg)

    def _get_sid(self):
        """
        Generator to provide the sid two times in case the first try
        failed. This can happen on an invalide or expired sid. In this
        case the sid gets regenerated for the second try.
        """
        yield self.sid
        self._set_sid_from_box()
        yield self.sid

    def _set_sid_from_box(self):
        """
        Read a session id from the box and store it in self.sid
        As long as self.sid holds a valid sid, the user is logged in.
        """
        with self.fc.session.get(self.login_url) as response:
            challenge = etree.fromstring(response.text).find('Challenge').text
        if challenge.startswith(PBKDF2_CHALLENGE_INDICATOR):
            challenge_hash = self._get_pbkdf2_hash(challenge)
        else:
            challenge_hash = self._get_md5_hash(challenge)
        self.sid = self._request_sid(challenge_hash)

    def _get_pbkdf2_hash(self, challenge):
        """Returns the vendor-recommended pbkdf2 challenge hash."""
        _, iterations_1, salt_1, iterations_2, salt_2 = challenge.split('$')
        static_hash = hashlib.pbkdf2_hmac(
            "sha256",
            self.fc.soaper.password.encode(),
            bytes.fromhex(salt_1),
            int(iterations_1)
        )
        dynamic_hash = hashlib.pbkdf2_hmac(
            "sha256",
            static_hash,
            bytes.fromhex(salt_2),
            int(iterations_2)
        )
        return f"{salt_2}${dynamic_hash.hex()}"

    def _get_md5_hash(self, challenge):
        """Returns the legathy md5 challenge hash."""
        hash = hashlib.md5(
            f"{challenge}-{self.fc.soaper.password}".encode("utf-16-le")
        )
        return f"{challenge}-{hash.hexdigest()}"

    def _request_sid(self, challenge_hash):
        """
        Takes the challenge_hash to request and return a new session id.
        """
        # TODO: handle blocktime
        with self.fc.session.post(
            self.login_url,
            data={"username": self.fc.soaper.user, "response": challenge_hash},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            root = etree.fromstring(response.text)
            sid_node = root.find("SID")
            return sid_node.text
