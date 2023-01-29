"""
Abstract base class for all library classes.

An internal module providing the `AbstractLibraryBase` class. This is an
abstract class that should not get instantiated but should serve as a
base class for library classes providing a common initialisation.

Also provides the FritzHttpMixin for homeautomation tasks that can not
be handled by the TR-064 interface.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer

import hashlib
from http import HTTPStatus

from ..core.fritzconnection import FritzConnection
from ..core.exceptions import FritzAuthorizationError, FritzConnectionException


class AbstractLibraryBase:
    """
    Abstract base class for library classes. Implements the common
    initialisation. The first argument `fc` can be a FritzConnection
    instance. If this argument is given no further arguments are needed.
    If the argument `fc` is not given, all other arguments are forwarded
    to get a FritzConnection instance. These arguments have the same
    meaning as for `FritzConnection.__init__()`. Using positional
    arguments is strongly discouraged. Use keyword arguments instead.
    """
    def __init__(self, fc=None, *args, **kwargs):
        if fc is None:
            fc = FritzConnection(*args, **kwargs)
        self.fc = fc

    @property
    def modelname(self):
        """
        The device modelname. Every library module derived from
        `AbstractLibraryBase` inherits this property.
        """
        return self.fc.modelname


class FritzHttpMixin:
    """
    Mixin for the AVM AHA-HTTP-Inferface.
    Provides the send_http_command() method for sending command
    via the aha-http-interface.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sid = None
        self.login_url = f"{self.fc.address}/login_sid.lua?version=2"
        self.homeauto_url = f"{self.fc.address}/webservices/homeautoswitch.lua"

    def send_http_command(self, command=None, identifier=None, **kwargs):
        """
        Send the command and the optional identifier to the http-interface
        and returns the content from the response as is.
        On error raises a FritzAuthorizationError if the error code was 403
        otherwise raises a generic FritzConnectionException with the
        corresponding error-code.
        """
        payload = {"switchcmd": command, "ain": identifier}
        payload.update(kwargs)
        for sid in self._get_sid():
            payload['sid'] = sid
            with self.fc.session.get(
                self.homeauto_url, params=payload
            ) as response:
                if response.status_code == HTTPStatus.OK:
                    return response.text
        msg = f"Request failed: http error code '{response.status_code}'"
        if response.status_code == HTTPStatus.FORBIDDEN:
            # should not happen because credentials are already
            # handled by the FritzConnection super-class
            raise FritzAuthorizationError(msg)
        raise FritzAHAInterfaceError(msg)

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
        if challenge.startswith("2$"):
            challenge_hash = self._get_pbkdf2_hash(challenge)
        else:
            challenge_hash = self._get_md5_hash(challenge)
        self.sid = self._request_sid(challenge_hash)

    def _get_pbkdf2_hash(self, challenge):
        """Returns vendor-recommended pbkdf2 challenge hash."""
        _, iterations_1, salt_1, iterations_2, salt_2 = challenge.split('$')
        static_hash = hashlib.pbkdf2_hmac(
            "sha256",
            fc.soaper.password.encode(),
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
        """Returns legathy md5 challenge hash."""
        hash = hashlib.md5(
            f"{challenge}-{self.fc.soaper.password}".encode("utf-16-le")
        )
        return f"{challenge}-{hash.hexdigest()}"

    def _request_sid(self, challenge_hash):
        """
        Takes the challenge_hash to request and return a new session id
        """
        with self.fc.session.post(
            self.login_url,
            data={"username": self.fc.soaper.user, "response": challenge_hash},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        ) as response:
            root = etree.fromstring(response.text)
            sid_node = root.find("SID")
            return sid_node.text
