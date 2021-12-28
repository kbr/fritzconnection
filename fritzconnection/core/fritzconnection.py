"""
Module to communicate with the AVM Fritz!Box.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import os
import string
import xml.etree.ElementTree as ElementTree

import requests
from requests.auth import HTTPDigestAuth

from .devices import DeviceManager
from .exceptions import (
    FritzResourceError,
    FritzServiceError,
)
from .soaper import Soaper

# disable InsecureRequestWarning from urllib3
# because of skipping certificate verification:
import urllib3

urllib3.disable_warnings()


# FritzConnection defaults:
FRITZ_IP_ADDRESS = "169.254.1.1"
FRITZ_TCP_PORT = 49000
FRITZ_TLS_PORT = 49443
FRITZ_USERNAME = "dslf-config"  # for Fritz!OS < 7.24
FRITZ_IGD_DESC_FILE = "igddesc.xml"
FRITZ_TR64_DESC_FILE = "tr64desc.xml"
FRITZ_DESCRIPTIONS = [FRITZ_IGD_DESC_FILE, FRITZ_TR64_DESC_FILE]
FRITZ_USERNAME_REQUIRED_VERSION = 7.24

# same defaults as used by requests:
DEFAULT_POOL_CONNECTIONS = 10
DEFAULT_POOL_MAXSIZE = 10

# supported protocols:
PROTOCOLS = ['http://', 'https://']


class FritzConnection:
    """
    Main class to set up a connection to the Fritz!Box router. All
    parameters are optional. `address` should be the ip of a router, in
    case that are multiple Fritz!Box routers in a network, the ip must
    be given. Otherwise, it is undefined which router will respond. If
    `user` and `password` are not provided, the environment gets checked for
    FRITZ_USERNAME and FRITZ_PASSWORD settings and taken from there, if
    found.

    The optional parameter `timeout` is a floating number in seconds
    limiting the time waiting for a router response. This is a global
    setting for the internal communication with the router. In case of a
    timeout a `requests.ConnectTimeout` exception gets raised.
    (`New in version 1.1`)

    `use_tls` accepts a boolean for using encrypted communication with
    the Fritz!Box. Default is `False`.
    (`New in version 1.2`)

    For some actions the Fritz!Box needs a password and since Fritz!OS
    7.24 also requires a username, the previous default username is just
    valid for OS versions < 7.24. In case the username is not given and
    the system version is 7.24 or newer, FritzConnection uses the last
    logged-in username as default.
    (`New in version 1.5`)

    For applications where the urllib3 default connection-pool size
    should get adapted, the arguments `pool_connections` and
    `pool_maxsize` can get set explicitly.
    (`New in version 1.6`)
    """

    def __init__(
        self,
        address=None,
        port=None,
        user=None,
        password=None,
        timeout=None,
        use_tls=False,
        pool_connections=DEFAULT_POOL_CONNECTIONS,
        pool_maxsize=DEFAULT_POOL_MAXSIZE,
    ):
        """
        Initialisation of FritzConnection: reads all data from the box
        and also the api-description (the servicenames and according
        actionnames as well as the parameter-types) that can vary among
        models and stores the information as instance-attributes.
        This can be an expensive operation. Because of this an instance
        of FritzConnection should be created once and reused in an
        application. All parameters are optional. But if there is more
        than one FritzBox in the network, an address (ip as string) must
        be given, otherwise it is not defined which box may respond. If
        no user is given the Environment gets checked for a
        FRITZ_USERNAME setting. If there is no entry in the environment
        the avm-default-username will be used. If no password is given
        the Environment gets checked for a FRITZ_PASSWORD setting. So
        password can be used without using configuration-files or even
        hardcoding. The optional parameter `timeout` is a floating point
        number in seconds limiting the time waiting for a router
        response. The timeout can also be a tuple for different values
        for connection- and read-timeout values: (connect timeout, read
        timeout). The timeout is a global setting for the internal
        communication with the router. In case of a timeout a
        `requests.ConnectTimeout` exception gets raised. `use_tls`
        accepts a boolean for using encrypted communication with the
        Fritz!Box. Default is `False`. `pool_connections` and `pool_maxsize`
        accept integers for changing the default urllib3 settings in order
        to modify the number of reusable connections.
        """
        if address is None:
            address = FRITZ_IP_ADDRESS
        if user is None:
            user = os.getenv("FRITZ_USERNAME", FRITZ_USERNAME)
        if password is None:
            password = os.getenv("FRITZ_PASSWORD", "")
        if port is None and use_tls:
            port = FRITZ_TLS_PORT
        elif port is None:
            port = FRITZ_TCP_PORT
        address = self.set_protocol(address, use_tls)

        # a session will speed up connections (significantly for tls)
        # and is required to change the default poolsize:
        session = requests.Session()
        session.verify = False
        if password:
            session.auth = HTTPDigestAuth(user, password)
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_connections, pool_maxsize=pool_maxsize)
        session.mount(PROTOCOLS[use_tls], adapter)
        # store as instance attributes for use by library modules
        self.address = address
        self.session = session
        self.timeout = timeout
        self.port = port

        self.soaper = Soaper(
            address, port, user, password, timeout=timeout, session=session
        )
        self.device_manager = DeviceManager(timeout=timeout, session=session)

        for description in FRITZ_DESCRIPTIONS:
            source = f"{address}:{port}/{description}"
            try:
                self.device_manager.add_description(source)
            except FritzResourceError:
                # resource not available:
                # this can happen on devices not providing
                # an igddesc-file.
                # ignore this
                pass

        self.device_manager.scan()
        self.device_manager.load_service_descriptions(address, port)
        # set default user for FritzOS >= 7.24:
        self._reset_user(user, password)


    def __repr__(self):
        """Return a readable representation"""
        return (
            f"{self.modelname} at {self.soaper.address}\n"
            f"FRITZ!OS: {self.system_version}"
        )

    @property
    def services(self):
        """
        Dictionary of service instances. Keys are the service names.
        """
        return self.device_manager.services

    @property
    def modelname(self):
        """
        Returns the modelname of the router.
        """
        return self.device_manager.modelname

    @property
    def system_version(self):
        """
        Returns system version if known, otherwise None.
        """
        return self.device_manager.system_version

    @staticmethod
    def normalize_name(name):
        """
        Returns the normalized service name. E.g. WLANConfiguration and
        WLANConfiguration:1 will get converted to WLANConfiguration1.
        """
        if ":" in name:
            name, number = name.split(":", 1)
            name = name + number
        elif name[-1] not in string.digits:
            name = name + "1"
        return name

    @staticmethod
    def set_protocol(url, use_tls):
        """
        Sets the protocol of the `url` according to the `use_tls`-flag
        and returns the modified `url`. Does not check whether the `url`
        given as parameter is correct.
        """
        url = url.split("//", 1)[-1]
        return PROTOCOLS[use_tls] + url

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
            response = self.call_action('LANConfigSecurity1', 'X_AVM-DE_GetUserList')
            root = ElementTree.fromstring(response['NewX_AVM-DE_UserList'])
            for node in root:
                if node.tag == 'Username' and node.attrib['last_user'] == '1':
                    last_user = node.text
                    break
            if last_user is not None:
                self.session.auth = HTTPDigestAuth(last_user, password)
                self.soaper.user = last_user
                self.soaper.session = self.session
                self.device_manager.session = self.session


    # -------------------------------------------
    # public api:
    # -------------------------------------------

    def call_action(self, service_name, action_name, *, arguments=None, **kwargs):
        """
        Executes the given action of the given service. Both parameters
        are required. Arguments are optional and can be provided as a
        dictionary given to 'arguments' or as separate keyword
        parameters. If 'arguments' is given additional
        keyword-parameters as further arguments are ignored.
        The argument values can be of type *str*, *int* or *bool*.
        (Note: *bool* is provided since 1.3. In former versions
        booleans must be provided as numeric values: 1, 0).
        If the service_name does not end with a number (like 1), a 1
        gets added by default. If the service_name ends with a colon and a
        number, the colon gets removed. So i.e. WLANConfiguration
        expands to WLANConfiguration1 and WLANConfiguration:2 converts
        to WLANConfiguration2.
        Invalid service names will raise a ServiceError and invalid
        action names will raise an ActionError.
        """
        arguments = arguments if arguments else dict()
        if not arguments:
            arguments.update(kwargs)
        service_name = self.normalize_name(service_name)
        try:
            service = self.device_manager.services[service_name]
        except KeyError:
            raise FritzServiceError(f'unknown service: "{service_name}"')
        return self.soaper.execute(service, action_name, arguments)

    def reconnect(self):
        """
        Terminate the connection and reconnects with a new ip.
        """
        self.call_action("WANIPConn1", "ForceTermination")

    def reboot(self):
        """
        Reboot the system.
        """
        self.call_action("DeviceConfig1", "Reboot")
