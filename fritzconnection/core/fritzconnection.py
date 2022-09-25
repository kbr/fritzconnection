"""
Module to communicate with the AVM Fritz!Box.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import json
import os
import pickle
import string
import xml.etree.ElementTree as ElementTree
from pathlib import Path

import requests
from requests.auth import HTTPDigestAuth

from .devices import DeviceManager
from .exceptions import (
    FritzConnectionException,
    FritzResourceError,
    FritzServiceError,
)
from .soaper import Soaper
from .utils import (
    get_bool_env,
    get_xml_root,
    localname
)

# disable InsecureRequestWarning from urllib3
# because of skipping certificate verification:
import urllib3

urllib3.disable_warnings()


# FritzConnection defaults:
FRITZ_IP_ADDRESS = "169.254.1.1"
FRITZ_TCP_PORT = 49000
FRITZ_TLS_PORT = 49443
FRITZ_USERNAME = "dslf-config"  # for Fritz!OS < 7.24
FRITZ_BOXINFO_FILE = "jason_boxinfo.xml"
FRITZ_IGD_DESC_FILE = "igddesc.xml"
FRITZ_TR64_DESC_FILE = "tr64desc.xml"
FRITZ_DESCRIPTIONS = [FRITZ_IGD_DESC_FILE, FRITZ_TR64_DESC_FILE]
FRITZ_USERNAME_REQUIRED_VERSION = 7.24
FRITZ_APPLICATION_ACCESS_DISABLED = """\n
    FRITZ!Box: access for applications disabled.
    Check: Home Network -> Network -> Network Settings
    for "Allow access for applications".\n"""
FRITZ_CACHE_DIR = ".fritzconnection"
FRITZ_CACHE_EXT = "_cache"
FRITZ_CACHE_JSON_SUFFIX = "json"
FRITZ_CACHE_PICKLE_SUFFIX = "pcl"
FRITZ_CACHE_FORMAT_JSON = "json"
FRITZ_CACHE_FORMAT_PICKLE = "pickle"
FRITZ_CACHE_FORMATS = {
    FRITZ_CACHE_FORMAT_JSON: FRITZ_CACHE_JSON_SUFFIX,
    FRITZ_CACHE_FORMAT_PICKLE: FRITZ_CACHE_PICKLE_SUFFIX
}
FRITZ_CACHE_UNKNOWN_FORMAT_MESSAGE = f"""\
    Unknown cache format "{{}}".\n
    Use one of {tuple(FRITZ_CACHE_FORMATS.keys())}.\n"""
FRITZ_ENV_USERNAME = "FRITZ_USERNAME"
FRITZ_ENV_PASSWORD = "FRITZ_PASSWORD"
FRITZ_ENV_USECACHE = "FRITZ_USECACHE"
FRITZ_ENV_CACHE_FORMAT = "FRITZ_CACHEFORMAT"
FRITZ_ENV_CACHEDIRECTORY = "FRITZ_CACHEDIRECTORY"

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

    The flag `use_cache` activates caching (default `False`). Caching
    can speed up instanciation significantly. The cached data are
    specific for the router ip, the router model and the installed
    FritzOS version. Multiple devices in the network can have separate
    cache-fies and can get used in parallel. By default the cache files
    are stored in the user home-directory in a `.fritzconnection`
    folder. To change this location use the parameter `cache_directory`
    providing a string or a `pathlib.Path` object. With `cache_format`
    two formats can specified for data serialization: `json` and
    `pickle`. These two values are available as constants
    `FRITZ_CACHE_FORMAT_JSON` and `FRITZ_CACHE_FORMAT_PICKLE`. Default
    is `pickle`. The flag `verify_cache` will enable cache verification
    (default is `True`). If set to `False` loading the api-data will be
    even faster, but the cache will not get renewed in case of FritzOS
    updates or a router change. All cache-settings can also configured
    in the environment: FRITZ_USECACHE (True|False), FRITZ_CACHEFORMAT
    (json|pickle) and FRITZ_CACHEDIRECTORY (a path).

    .. versionadded:: 1.10
    """

    def __init__(
        self,
        address=None,
        port=None,
        user=None,
        password=None,
        timeout=None,
        use_tls=False,
        use_cache=False,
        verify_cache=True,
        cache_directory=None,
        cache_format=None,
        pool_connections=DEFAULT_POOL_CONNECTIONS,
        pool_maxsize=DEFAULT_POOL_MAXSIZE,
    ):
        """
        Initialisation of FritzConnection: reads all data from the box
        and also the api-description (the servicenames and according
        actionnames as well as the parameter-types) that can vary among
        models and stores the information as instance-attributes. This
        can be an expensive operation. Because of this an instance of
        FritzConnection should be created once and reused in an
        application.

        All parameters are optional. But if there is more than one
        FritzBox in the network, an address (ip as string) must be
        given, otherwise it is not defined which box may respond. If no
        user is given the Environment gets checked for a FRITZ_USERNAME
        setting. If there is no entry in the environment the
        avm-default-username will be used. If no password is given the
        Environment gets checked for a FRITZ_PASSWORD setting. So
        password can be used without using configuration-files or even
        hardcoding.

        The optional parameter `timeout` is a floating point number in
        seconds limiting the time waiting for a router response. The
        timeout can also be a tuple for different values for connection-
        and read-timeout values: (connect timeout, read timeout). The
        timeout is a global setting for the internal communication with
        the router. In case of a timeout a `requests.ConnectTimeout`
        exception gets raised.

        `use_tls` accepts a boolean for using encrypted communication
        with the Fritz!Box. Default is `False`.

        `use_cache` is a boolean whether a cache should get used for the
        router api data. By default the api data are loaded from the
        router at instanciation time what can take several seconds to
        complete. `cache_directory` is the path to the directory storing
        the cached data. By default this is a folder named
        '.fritzconnection' in the users home-directory. `cache_format`
        supports two file-formats: json and pickle (default). All cache
        settings can also defined in the environment: FRITZ_USECACHE
        (True|False), FRITZ_CACHEFORMAT (json|pickle) and
        FRITZ_CACHEDIRECTORY (a path).

        If `verify_cache` is `True` it checks whether the model has
        changed or the system software has got an update. In this case
        the cache gets renewed. Default is `True`. Deactivating the
        verification gives another gain in speed, but on updates and
        other changes you are on your own.

        `pool_connections` and `pool_maxsize` accept integers for
        changing the default urllib3 settings in order to modify the
        number of reusable connections.
        """
        if address is None:
            address = FRITZ_IP_ADDRESS
        if user is None:
            user = os.getenv(FRITZ_ENV_USERNAME, FRITZ_USERNAME)
        if password is None:
            password = os.getenv(FRITZ_ENV_PASSWORD, "")
        if use_cache is None:
            use_cache = get_bool_env(FRITZ_ENV_USECACHE)
        if cache_format is None:
            cache_format = os.getenv(
                FRITZ_ENV_CACHE_FORMAT, FRITZ_CACHE_FORMAT_PICKLE
            )
        if cache_directory is None:
            cache_directory = os.getenv(FRITZ_ENV_CACHEDIRECTORY, None)
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
        # cache for updatecheck as @functools.cached_property
        # needs Python >= 3.8:
        self._updatecheck = None
        # store as instance attributes for use by library modules
        self.address = address
        self.session = session
        self.timeout = timeout
        self.port = port

        self.soaper = Soaper(
            address, port, user, password, timeout=timeout, session=session
        )
        self.device_manager = DeviceManager(timeout=timeout, session=session)
        self._load_router_api(
            use_cache, cache_directory, cache_format, verify_cache
        )
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

    @property
    def device_description(self):
        """
        Returns a string with the device description. This is a
        combination of the device model name and the installed software
        version.
        """
        return self.call_action("DeviceInfo1", "GetInfo")["NewDescription"]

    @property
    def updatecheck(self):
        """
        Dictionary with information about the hard- and software version of
        the device according to "http://fritz.box/jason_boxinfo.xml".
        """
        if self._updatecheck is None:
            xml_data = get_xml_root(
                f"{self.address}/{FRITZ_BOXINFO_FILE}",
                timeout=self.timeout,
                session=self.session
            )
            self._updatecheck = {
                localname(elem): elem.text for elem in xml_data
            }
        return self._updatecheck

    @staticmethod
    def normalize_name(name):
        """
        Returns the normalized service name. E.g. `WLANConfiguration` and
        `WLANConfiguration:1` will get converted to `WLANConfiguration1`.
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
                self.device_manager.session = self.session

    # -------------------------------------------
    # public api:
    # -------------------------------------------

    def call_action(
        self,
        service_name,
        action_name,
        *,
        arguments=None,
        **kwargs
    ):
        """
        Executes the given action of the given service. Both parameters
        are required. Arguments are optional and can be provided as a
        dictionary given to 'arguments' or as separate keyword
        parameters. If 'arguments' is given additional
        keyword-parameters as further arguments are ignored.

        The argument values can be of type *str*, *int* or *bool*.
        (Note: *bool* is provided since 1.3. In former versions booleans
        must be provided as numeric values: 1, 0).

        If the service_name does not end with a number-character (like
        "1""), a "1" gets added by default. If the service_name ends
        with a colon and a number, the colon gets removed. So i.e.
        "WLANConfiguration" expands to "WLANConfiguration1" and
        "WLANConfiguration:2" converts to "WLANConfiguration2"". Invalid
        service names will raise a ServiceError and invalid action names
        will raise an ActionError.
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

    # -------------------------------------------
    # internal methods to load router-api:
    # -------------------------------------------

    def _load_router_api(
        self,
        use_cache=False,
        cache_directory=None,
        cache_format=FRITZ_CACHE_FORMAT_JSON,
        verify_cache=True,
    ):
        """
        Load the router api.

        If `use_cache` is `False`, load the api from the router. If
        `use_cache` is `True``, the api data are loaded from a file,
        which is in pickle or json format, according to the setting of
        `cache_format`.  The file location can get set by the argument
        `cache_directory`. If `cache_directory` is not given, the
        default-directory is used (which is in most cases a subdirectory
        of the user home directory). After loading from a file the
        cached data are checked to detect a software-update or a change
        of the router model. If this check fails, the api gets reloaded
        from the router and the cache data are updated. The same happens
        on errors loading the cache-file.
        """
        def reload_api():
            # reset in case of remaining artefacts:
            self.device_manager.descriptions = []
            self.device_manager.services = {}
            # reload and save again:
            self._load_api_from_router()
            self._write_api_to_cache(path, cache_format)

        if use_cache:
            path = self._get_cache_path(cache_directory, cache_format)
            try:
                self._load_api_from_cache(path, cache_format)
            except FileNotFoundError:
                # can happen i.e. on first run
                reload_api()
            else:
                if verify_cache and not self._is_valid_cache():
                    # can happen on model changes or software updates
                    reload_api()
        else:
            self._load_api_from_router()

    def _is_valid_cache(self):
        """
        Checks whether the cache-data seems to be valid. Returns a
        booean: `True` if valid, `False` otherwise.
        """
        # system_id is something like ('FRITZ!Box 7590', '154.07.29') which
        # originates from the device description and is part of the cache data.
        cached_id = (
            self.device_manager.modelname,
            self.device_manager.system_info[-1]
        )
        # retrive the same information from the updatecheck property.
        # If the result is the same, the cache-data can considered as valid.
        try:
            device_info = self.updatecheck
        except FritzConnectionException:
            # something went wrong, cache data can not be verified:
            # should never happen with a connected device.
            return False
        current_id = (
            device_info['Name'],
            device_info['Version']
        )
        return cached_id == current_id

    def _get_cache_path(self, cache_directory, cache_format):
        """
        Returns the path to the cache file (including the filename and
        extension) as a Path instance.
        """
        # ignore optional scheme:
        address = self.address.split('//')[-1]
        address = address.replace(".", "_")
        try:
            suffix = FRITZ_CACHE_FORMATS[cache_format]
        except KeyError:
            message = FRITZ_CACHE_UNKNOWN_FORMAT_MESSAGE.format(cache_format)
            raise FritzConnectionException(message)
        filename = f"{address}{FRITZ_CACHE_EXT}.{suffix}"
        if cache_directory:
            return Path(cache_directory) / filename
        return Path().home() / FRITZ_CACHE_DIR /filename

    def _write_api_to_cache(self, path, cache_format):
        """
        Stores the api data in a cache-file.
        """
        binary = "wb"
        text = "wt"
        mode = binary if cache_format == FRITZ_CACHE_FORMAT_PICKLE else text
        with open(path, mode) as fobj:
            if mode == binary:
                pickle.dump(self.device_manager.descriptions, fobj)
            else:
                json.dump(self.device_manager.serialize(), fobj)

    def _load_api_from_cache(self, path, cache_format):
        """
        Read the api data from a cache-file and forwards the data to the
        device_manager.
        Currently two formats are supported: `pickle` and `json`. If
        `cache_format` is not `pickle` it is assumed that the format is
        `json`.
        Raise a FileNotFoundError in case of an invalide path.
        """
        binary = "rb"
        text = "rt"
        mode = binary if cache_format == FRITZ_CACHE_FORMAT_PICKLE else text
        with open(path, mode) as fobj:
            if mode == binary:
                self.device_manager.descriptions = pickle.load(fobj)
            else:
                self.device_manager.deserialize(json.load(fobj))
        self.device_manager.scan()

    def _load_api_from_router(self):
        """
        Read the api data from the router and forwards the data to the
        device_manager.
        """
        for description in FRITZ_DESCRIPTIONS:
            source = f"{self.address}:{self.port}/{description}"
            try:
                self.device_manager.add_description(source)
            except FritzResourceError:
                # resource not available:
                # this can happen on devices not providing
                # an igddesc-file.
                # ignore this
                # But if the "tr64desc.xml" file is missing the router
                # may not have TR-064 activated. In this case raise a
                # useful error-message.
                if description == FRITZ_TR64_DESC_FILE:
                    raise FritzConnectionException(
                        FRITZ_APPLICATION_ACCESS_DISABLED
                    )
        self.device_manager.scan()
        self.device_manager.load_service_descriptions(self.address, self.port)
