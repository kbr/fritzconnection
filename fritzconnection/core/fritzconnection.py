"""
Module to communicate with the AVM Fritz!Box.
"""
"""
changelog v2.0:

    argument `use_cache` now defaults to True
    argument `verify_cache` removed
    argument `cache_format` removed
"""

import os
import string

import requests

from pathlib import Path
from requests.auth import HTTPDigestAuth
from typing import Any

from fritzconnection import __version__
from fritzconnection.core.description import Service
from fritzconnection.core.exceptions import FritzServiceError
from fritzconnection.core.fritzdescription import FritzDescription
from fritzconnection.core.fritzhttp import FritzHttp
from fritzconnection.core.soaper import Soaper

# FritzConnection defaults:
FRITZ_IP_ADDRESS = "169.254.1.1"
FRITZ_TCP_PORT = 49000
FRITZ_TLS_PORT = 49443
FRITZ_USERNAME = "dslf-config"  # for Fritz!OS < 7.24
FRITZ_USERNAME_REQUIRED_VERSION = 7.24

FRITZ_ENV_IPADDRESS = "FRITZ_IPADDRESS"
FRITZ_ENV_PORT = "FRITZ_PORT"
FRITZ_ENV_TLS_PORT = "FRITZ_TLS_PORT"
FRITZ_ENV_USERNAME = "FRITZ_USERNAME"
FRITZ_ENV_PASSWORD = "FRITZ_PASSWORD"
FRITZ_ENV_CACHEDIRECTORY = "FRITZ_CACHEDIRECTORY"


# same defaults as used by requests:
DEFAULT_POOL_CONNECTIONS = 10
DEFAULT_POOL_MAXSIZE = 10

import urllib3
urllib3.disable_warnings()


def get_argument(value, env_name, default):
    if not value:
        value = os.getenv(env_name, default)
    return value


class FritzConnection:
    """
    Main class to set up a connection to the Fritz!Box router. All
    parameters are optional. `address` should be the ip of a router, in
    case that are multiple Fritz!Box routers in a network, the ip must
    be given. Otherwise, it is undefined which router will respond. If
    `user` and `password` are not provided, the environment gets checked for
    FRITZ_USERNAME and FRITZ_PASSWORD settings and taken from there, if
    found.

    Basic usage assuming `user` and `password` stored in the environment:

    >>> fc = FritzConnection(address="192.168.178.1")
    >>> fc.call_action("WANIPConn1", "ForceTermination", arguments={})

    This will reconnect the router with the external network.
    `arguments` is not necessary here, but in case where arguments must
    be provided, this is done by `arguments` (see also the documentation
    for the `call_action()`` method`). The `call_action()` method is
    used for the TR-064 API and returns a dictionary with the results.

    For accessing the http-interface (aka AHA-HTTP-Interface) of the
    router, FritzConnection provides the `call_http()` method (added in
    version 1.12). As arguments this method takes a required command
    (like `getswitchlist`) and optional parameters as described in the
    AVM documentation:

    >>> fc.call_http("getswitchlist")

    This method triggers a http response and returns a dictionary with
    three key-value pairs: the `content-type`, the `encoding` and the
    `content` itself. The values are all of type string. The
    content-type is typically "text/plain" or "text/xml", the encoding,
    typically "utf-8".

    The method will raise a FritzAuthorizationError in case of missing
    credentials. In case of an unknown command or identifier a
    FritzHttpInterfaceError will get raised.

    .. versionadded:: 1.12

    The optional parameter `timeout` is a floating number in seconds
    limiting the time waiting for a router response. This is a global
    setting for the internal communication with the router. In case of a
    timeout a `requests.ConnectTimeout` exception gets raised.

    .. versionadded:: 1.1

    `use_tls` accepts a boolean for using encrypted communication with
    the Fritz!Box. Default is `False`.

    .. versionadded:: 1.2

    For some actions the Fritz!Box needs a password and since Fritz!OS
    7.24 also requires a username, the previous default username is just
    valid for OS versions < 7.24. In case the username is not given and
    the system version is 7.24 or newer, FritzConnection uses the last
    logged-in username as default.

    .. versionadded:: 1.5

    For applications where the urllib3 default connection-pool size
    should get adapted, the arguments `pool_connections` and
    `pool_maxsize` can get set explicitly.

    .. versionadded:: 1.6

    The flag `use_cache` activates caching (default `True` - changed
    from False to True in version 2.0). Caching can speed up
    instantiation significantly. The cached data are specific for the
    router ip, the router model and the installed FritzOS version.
    Multiple devices in the network can have separate cache-fies and can
    get used in parallel.

    .. versionadded:: 1.10

    `cache_directory`: can be a string or Path-object to change to
    location of the cache-files. By default the cache files are stored
    in the user home-directory in a `.fritzconnection` folder. The
    cache-directory can also be set in the environment with
    FRITZ_CACHEDIRECTORY (absolute path as string).

    .. versionadded:: 1.10

    `redact_debug_log` accepts a boolean for enabling redacting sensitiv
    data (i.e. phone numbers) in debug outputs. Default is `False`.

    .. versionadded:: 1.15
    
    `use_cache` now defaults to `True`. `cache_format` has been removed.
    
    .. versionadded:: 2.0

    """

    def __init__(
        self,
        address: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        timeout: float | None = None,
        use_tls: bool = False,
        use_cache: bool = True,
        cache_directory: str | Path | None = None,
        pool_connections: int = DEFAULT_POOL_CONNECTIONS,
        pool_maxsize: int = DEFAULT_POOL_MAXSIZE,
        redact_debug_log: bool = False
    ):
        self.ip_address = get_argument(address, FRITZ_ENV_IPADDRESS, FRITZ_IP_ADDRESS)
        self.user = get_argument(user, FRITZ_ENV_USERNAME, FRITZ_USERNAME)
        self.password = get_argument(password, FRITZ_ENV_PASSWORD, "")
        if use_tls:
            port = get_argument(port, FRITZ_ENV_TLS_PORT, FRITZ_TLS_PORT)
            protocol = "https://"
        else:
            port = get_argument(port, FRITZ_ENV_PORT, FRITZ_TCP_PORT)
            protocol = "http://"
        self.port = port
        self.protocol = protocol
        self.address = f"{self.protocol}{self.ip_address}:{self.port}"

        # keep cache_directory as None if not set
        # default will get set in FritzDescription
        cache_directory = get_argument(cache_directory, FRITZ_ENV_CACHEDIRECTORY, None)

        # a session will speed up connections (significantly for tls)
        # and is required to change the default poolsize:
        session = requests.Session()
        session.verify = False
        if self.password:
            session.auth = HTTPDigestAuth(self.user, self.password)
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_connections,
            pool_maxsize=pool_maxsize
        )
        session.mount(self.protocol, adapter)
        self.session = session

        # the Soaper is the interface for the TR64-Services (via soap)
        self.soaper = Soaper(
            self.address, self.user, self.password,
            timeout=timeout, session=session, redact_debug_log=redact_debug_log
        )

        self.description = FritzDescription(
            ip_address=self.ip_address,
            uri=self.address,  # TODO: is uri a missleading name?
            session=session,
            timeout=timeout,
            use_cache=use_cache,
            cache_directory=cache_directory
        )
        self.description.load_descriptions()

        # set default user for FritzOS >= 7.24:
        #self._reset_user(user, password)
        # provide the http-interface
        self.http_interface = FritzHttp(self)
        
    def __str__(self):
        return (
            f"{self.__class__.__name__} [version {__version__}]\n"
            f"Device: {self.device_name}\n"
            f"System: {self.system_version}"
        )

    def _reset_user(self, user, password):
        """
        For Fritz!OS >= 7.24: if a password is given and the username is
        the historic FRITZ_USERNAME, then check for the last logged-in
        username and use this username for the soaper. Also recreate the
        session used by the soaper and the device_manager.

        This may not guarantee a valid user/password combination, but is
        the way AVM recommends setting the required username in case a
        username is not provided.
        """
        try:
            sys_version = float(self.system_version)
        except (ValueError, TypeError):
            # version not available: don't do anything
            return
        if (sys_version >= FRITZ_USERNAME_REQUIRED_VERSION
            and user == FRITZ_USERNAME
            and password
        ):
            last_user = None
            response = self.call_action(
                'LANConfigSecurity1', 'X_AVM-DE_GetUserList'
            )
            root = ElementTree.fromstring(response['NewX_AVM-DE_UserList'])
            for node in root:
                if node.tag == 'Username' and node.attrib['last_user'] == '1':
                    last_user = node.text
                    break
            if last_user is not None:
                self.session.auth = HTTPDigestAuth(last_user, password)
                self.soaper.user = last_user
                self.soaper.session = self.session
                self.description.session = self.session

    @staticmethod
    def _get_normalized_service_name(name):
        """
        Returns the normalized service name, i.e. `WLANConfiguration` or
        `WLANConfiguration:1` will get converted to `WLANConfiguration1`.
        """
        if ":" in name:
            name, number = name.split(":", 1)
            name = f"{name}{number}"
        elif name[-1] not in string.digits:
            name = f"{name}1"
        return name

    @property
    def device_name(self) -> str:
        """
        Returns the name of the device.
        """
        return self.description.device_name
        
    @property
    def modelname(self) -> str:
        """
        Returns the name of the device.
        
        .. version-deprecated:: 2.0
           Use :py:func:`device_name` instead.
        """
        return self.device_name
    
    @property
    def has_wan_support(self) -> bool:
        """
        True if the device support a WAN interface.
        """
        return "Layer3Forwarding1" in self.description.services
        
    @property
    def has_mesh_support(self) -> bool:
        """
        True if the device supports mesh, otherwise False.
        """
        return "X_AVM-DE_GetMeshListPath" in self.description.services["Hosts1"].actions

    @property
    def system_version(self) -> str:
        """
        Returns system version if known.
        """
        return self.description.system_version
        
    @property
    def services(self) -> dict[str, Service]:
        """
        Returns a dictionary with the available services. The keys are
        the service-names and the values are the service-instances.
        """
        return self.description.services

    def call_action(
        self,
        service_name: str,
        action_name: str,
        *,
        arguments: dict | None = None,
        **kwargs
    ) -> dict[str, Any]:
        """
        Makes a tr64-call by calling the action of the given service.
        Both arguments `servive_name` and `action_name` are required.
        `arguments` is an optional dictionary with arguments send to the
        action. Arguments can also be provided as keyword-arguments. If
        an arguments-dictionary and keyword-arguments are given, they
        will get combined. A keyword argument with the same name as an
        argument in the `arguments` dictionary will overwrite the value
        in the dictionary.
        
        The values in the `arguments` dictionary can be of type *str*,
        *int* or *bool*. (Note: *bool* is provided since 1.3. In former
        versions booleans must be provided as numeric values: 1, 0).

        Invalid service names will raise a ServiceError and invalid
        action names will raise an ActionError.

        Legathy-feature: If the service_name does not end with a digit
        (like "1"), a "1" gets added by default. If the service_name
        ends with a colon and a digit, the colon gets removed. So i.e.
        "WLANConfiguration" expands to "WLANConfiguration1" and
        "WLANConfiguration:2" converts to "WLANConfiguration2".
        Newer code should avoid this calling style.
        
        The method returns a dictionary with argument-names as keys and
        the corresponding information as values. Numeric and boolean
        values are converted from strings to Python datatypes.
        """
        arguments = arguments if arguments else {}
        arguments.update(kwargs)
        service_name = self._get_normalized_service_name(service_name)
        try:
            service = self.description.services[service_name]
        except KeyError:
            raise FritzServiceError(f'unknown service: "{service_name}"')
        return self.soaper.execute(service, action_name, arguments)
    
    def call_http(
        self,
        command: str,
        identifier: str | None = None,
        **kwargs
    ) -> dict[str, str]:
        """
        Executes the given command according to the AHA-HTTP-Interface.
        The `identifier` represents the `ain` of a target-device.
        `kwargs` can hold additional parameters depending on the device.

        The method returns a dictionary of strings with three items: the
        `content-type`, the `encoding` and the corresponding result (the
        `content`). The content-type is typically "text/plain" or
        "text/xml", the encoding, typically "utf-8".

        The method will raise a FritzAuthorizationError in case of
        missing credentials. In case of an unknown command or identifier
        a FritzHttpInterfaceError will get raised.

        .. versionadded:: 1.12
        """
        header, content = self.http_interface.execute(
            command,
            identifier,
            **kwargs
        )
        content_type, charset = [item.strip() for item in header.split(";")]
        # extract the encoding from the charset-information
        encoding = charset.split("=")[-1].strip()
        return {
            "content-type": content_type,
            "encoding": encoding,
            "content": content
        }
        
    def call_rest_api(self, method, path, base_path=None, payload=None):
        """
        Returns a response instance (from the requests library) with the
        result of the call. 
        """
        return self.http_interface.call_rest_api(method, path, base_path, payload)

    def get_cpu_temperatures(self) -> list[int]:
        """
        Returns a list of the last measured cpu-temperatures.
        The most recent entry is the first one in the list.
        NOTE: this function call is experimental as it is based on a
        non-public API. It may work or not and may get removed if the
        API changes (even without a deprecation warning).
        """
        return self.http_interface.get_cpu_temperatures()
      
    def reboot(self) -> None:
        """
        Reboot the system.
        """
        self.call_action("DeviceConfig1", "Reboot")
