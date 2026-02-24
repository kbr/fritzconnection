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
from xml.etree import ElementTree as etree

from fritzconnection.core.exceptions import FritzAuthorizationError
from fritzconnection.core.exceptions import FritzHttpInterfaceError
from fritzconnection.core.fritz_sid import FritzSID
from fritzconnection.core.utils import get_xml_root


BASE_LOGIN_URL = "/login_sid.lua"
URL_LOGIN = f"{BASE_LOGIN_URL}?version=2"
URL_HOMEAUTOSWITCH = "/webservices/homeautoswitch.lua"


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
        
    def call_rest_api(self, method, path, base_path="api/v0", payload=None):
        """
        Makes a low level-call to the router REST-API.
        Takes a method like i.e. `GET` or `POST`. An unimplemented
        method will raise a KeyError. Depending on the REST-API call
        `path` and `payload` must match.
        Returns a response object (which is a Requests response).
        """
        calls = {
            "GET": self.fc.session.get,
            "POST": self.fc.session.post,
        }
        call = calls[method.upper()]
        url = f"{self.router_url}/{base_path}/{path}"
        headers = {
            'Authorization': self.get_sid(),
            'Content-Type': "application/json",
        }
        with call(url, params=payload, headers=headers, verify=False) as response:
            return response
        
    def get_sid(self):
        """
        Returns a new valid session id.
        """
        return self.fs.get_session_id()
