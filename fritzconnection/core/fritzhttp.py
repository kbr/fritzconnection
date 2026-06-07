"""
fritzhttp.py

Access the AVM Fritz!Box AHA-HTTP-Interface
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


from http import HTTPStatus
from http.client import HTTP_PORT

from contextlib import contextmanager

from fritzconnection.core.exceptions import FritzAuthorizationError
from fritzconnection.core.exceptions import FritzHttpInterfaceError
from fritzconnection.core.fritz_sid import FritzSID


BASE_LOGIN_URL = "/login_sid.lua"
URL_LOGIN = f"{BASE_LOGIN_URL}?version=2"
URL_HOMEAUTOSWITCH = "/webservices/homeautoswitch.lua"
REST_API_BASEPATH = "api/v0"
AUTHORIZATION_PREFIX = "AVM-SID"


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
        self.fs = FritzSID(fc)

    @contextmanager
    def _digest_auth_disabled(self):
        """Temporarily disable digest auth on the shared requests session."""
        old_auth = self.fc.session.auth
        self.fc.session.auth = None
        try:
            yield
        finally:
            self.fc.session.auth = old_auth

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
    def router_url(self):
        """Returns the combination of router address and port."""
        return f"{self.fc.protocol}{self.fc.ip_address}:{self.remote_port}"

    @property
    def login_url(self):
        """The login-url including protocol and configurable port."""
        return f"{self.router_url}{URL_LOGIN}"

    @property
    def homeauto_url(self):
        """The homeauto-url including protocol and configurable port."""
        return f"{self.router_url}{URL_HOMEAUTOSWITCH}"

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
        response = self.call_url(self.homeauto_url, payload)
        return response.headers.get('content-type'), response.text

    def call_url(self, url, payload):
        """
        Makes a call to the router with the provided url. Returns the
        request object in case of success. Otherwise a
        FritzHttpInterfaceError will get raised.

        Beside the public API documented by AVM this method allows calls
        to undocumented APIs serving the router web-interface or
        providing other data.

        WARNING: For a reliable application it is highly discouraged to
        use undocumented endpoints because they can change any time without
        notice. So an application may not survive a router OS update.
        """
        payload['sid'] = self.get_sid()
        with self.fc.session.get(url, params=payload) as response:
            if response.status_code == HTTPStatus.OK:
                return response

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
        
    def call_rest_api(
        self, 
        method, 
        path, 
        base_path=None, 
        path_extension=None,
        params=None,
        payload=None,
        extra_headers: dict[str, str] | None = None,
    ):
        """
        Makes a low level-call to the router REST-API. Takes a method
        like i.e. `GET` or `POST`. An unimplemented method will raise a
        KeyError. Depending on the REST-API call `path` and `path_extension`
        must match. `path_extension` can be a UID or a serial, depending on
        the call. If payload is given it should be an object convertible
        to json (typically a dict). All given arguments are expected to
        follow the openapi 3 specification.
        `extra_headers`: Optional additional request headers for this
        endpoint (e.g. `Origin`, `Referer` for WebUI-like REST endpoints).
        `Authorization` is always derived from SID and not overridden by
        `extra_headers`.

        Returns a response object (from the `requests` library) with
        `status_code` and `text` as properties (or `json()` as callable).
        """
        if base_path is None:
            base_path = REST_API_BASEPATH
        calls = {
            "GET": self.fc.session.get,
            "PUT": self.fc.session.put,
            "POST": self.fc.session.post,
            "DEL": self.fc.session.delete,
        }
        call = calls[method.upper()]
        url = f"{self.router_url}/{base_path}/{path}"
        if path_extension:
            url = f"{url}/{path_extension}"
        sid = self.get_sid()
        rest_headers = {
            'Authorization': f"{AUTHORIZATION_PREFIX} {sid}",
        }
        if payload:
            rest_headers["content-type"] = "application/json"
        if extra_headers is not None:
            # The REST layer can be reused for WebUI endpoints that require
            # additional browser-like headers (e.g. Origin/Referer).
            # Keep Authorization from being overridden accidentally.
            rest_headers.update(extra_headers)
            rest_headers["Authorization"] = f"{AUTHORIZATION_PREFIX} {sid}"

        # Disable digest auth on the shared requests session because REST
        # calls use SID in Authorization. Digest auth can otherwise interfere
        # with the WebUI endpoints.
        with self._digest_auth_disabled():
            with call(
                url,
                headers=rest_headers,
                params=params,
                json=payload,
                verify=False,
            ) as response:
                return response
        
    def get_sid(self):
        """
        Returns a new valid session id.
        """
        return self.fs.get_session_id()
