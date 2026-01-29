"""
Loads the description files from the device describing the API. A device
can be a router or a repeater.
"""

import pathlib
import pickle

from fritzconnection.core.description import BoxInfo
from fritzconnection.core.description import SCPD
from fritzconnection.core.description import TR64Description
from fritzconnection.core.description import UPnPInternetGatewayDescription
from fritzconnection.core.exceptions import FritzResourceError
from fritzconnection.core.utils import get_xml_root


FRITZ_BOXINFO_FILE = "jason_boxinfo.xml"
FRITZ_IGD_DESC_FILE = "igddesc.xml"
FRITZ_TR64_DESC_FILE = "tr64desc.xml"
FRITZ_CACHE_DIR = ".fritzconnection"
FRITZ_CACHE_EXT = ".cache"
IGD_DEVICE = "igd_device"
TR64_DEVICE = "tr64_device"


class FritzDescription:
    """
    Description wrapper class for the device information. The arguments
    are:

    `ip_address`: internal ip-address of the device as string.
    `uri`: the ip_address with the http-protocol as prefix and the port
    as postfix.
    `session`: the requests.Session object
    `use_cache`: boolean whether to use the cache, defaults to True

    All arguments are optional for testing
    """

    def __init__(self, ip_address=None, uri=None, session=None, timeout=None,
                 use_cache=True, cache_directory=None):
        self.descriptions = {
            IGD_DEVICE: UPnPInternetGatewayDescription(),
            TR64_DEVICE: TR64Description()
        }
        self.ip_address = ip_address
        self.uri = uri
        self.session = session
        self.timeout = timeout
        self.use_cache = use_cache
        self.cache_directory = cache_directory
        self._services = {}
        self._boxinfo = None

    def __eq__(self, other):
        """
        This is implemented for testing. Two instances are assumed to be
        equal if the descriptions are the same (which are dataclasses
        and comparable).
        """
        return (
            self.descriptions[IGD_DEVICE] == other.descriptions[IGD_DEVICE]
            and self.descriptions[TR64_DEVICE] == other.descriptions[TR64_DEVICE]
        )

    @property
    def igd_services(self):
        return self.descriptions[IGD_DEVICE].services

    @property
    def tr64_services(self):
        return self.descriptions[TR64_DEVICE].services

    @property
    def services(self) -> dict:
        """
        Returns a dictionary with the provided services of the device.
        The keys are the service-names, the values are the
        service-objects.
        """
        if not self._services:
            for description in self.descriptions.values():
                self._services.update(description.services)
        return self._services

    @property
    def device_name(self):
        """
        Returns the name of the tr064 device
        """
        return self.descriptions[TR64_DEVICE].device_name

    def get_boxinfo(self, source=None):
        if self._boxinfo is None:
            if source is None:
                # uri without the port because
                # FRITZ_BOXINFO_FILE is provided via port 80
                uri, _ = self.uri.rsplit(":", 1)
                source = f"{uri}/{FRITZ_BOXINFO_FILE}"
            root = get_xml_root(source, session=self.session)
            self._boxinfo = BoxInfo()
            self._boxinfo.load(root)
        return self._boxinfo

    @property
    def system_version(self):
        version = self.descriptions[TR64_DEVICE].system_version
        if not version:
            # try to get the version from boxinfo:
            boxinfo = self.get_boxinfo()
            version = boxinfo.version
        return version

    def load_descriptions(self):
        if self.use_cache:
            self.load_descriptions_from_cache()
        else:
            self.load_descriptions_from_device()

    def load_scpd_data(self):
        for service in self.services.values():
            scpd_source = self.uri + service.SCPDURL
            scpd = SCPD()
            try:
                root = get_xml_root(
                    scpd_source, session=self.session, timeout=self.timeout
                )
            except FritzResourceError:
                # unable to read the requestet resource: skip this
                pass
            else:
                scpd.load(root)
            service.scpd = scpd

    def load_descriptions_from_cache(self) -> None:
        """
        Loads the description data from cache. In case this fails or the
        cache is invalid, load the descriptions from the device and
        store the data again in a cache-file.
        """
        if self.load_cache():
            if self.check_cache():
                return None
        self.load_descriptions_from_device()
        self.store_cache()

    def load_descriptions_from_device(self):
        uri = self.uri if self.uri.endswith("/") else f"{self.uri}/"
        igd_source = uri + FRITZ_IGD_DESC_FILE
        tr64_source = uri + FRITZ_TR64_DESC_FILE
        self.load_descriptions_from_source(igd_source, tr64_source)

    def load_descriptions_from_source(self, igd_source=None, tr64_source=None):
        """
        Internal method to load the description information from the
        given sources. Because reading the sources is delegated to
        `get_xml_root` the sources can be an xml-string, a file-name a
        Path object or an uri. This makes the method testable.
        """
        # create new descriptions in case of remaining
        # invalide cache data:
        self.descriptions[IGD_DEVICE] = UPnPInternetGatewayDescription()
        self.descriptions[TR64_DEVICE] = TR64Description()
        if igd_source:
            try:
                root = get_xml_root(
                    igd_source, session=self.session, timeout=self.timeout
                )
            except FritzResourceError:
                # can happen if the device does not support
                # an igd_file (i.e. it is not a WAN device)
                pass
            else:
                self.descriptions[IGD_DEVICE].load(root)
        if tr64_source:
            # it is an error if this source is not available
            root = get_xml_root(tr64_source, session=self.session, timeout=self.timeout)
            self.descriptions[TR64_DEVICE].load(root)
        # after loading the services load the scpd-data,
        # but don't do this if self.uri is None
        # (happen by testing with files)
        if self.uri:
            self.load_scpd_data()

    def store_cache(self):
        """
        Store the pickled description data.
        """
        path = self._get_cache_path()
        with open(path, "wb") as fobj:
            pickle.dump(self.descriptions, fobj)

    def load_cache(self) -> bool:
        """
        Loads the cached data into self.descriptions. Returns False if
        there was no cache-file, otherwise returns True.
        """
        path = self._get_cache_path()
        try:
            with open(path, "rb") as fobj:
                self.descriptions = pickle.load(fobj)
        except FileNotFoundError:
            result = False
        else:
            result = True
        return result

    def check_cache(self, source=None) -> bool:
        """
        Assumes the description data are loaded. Then the boxinfo gets
        loaded from the given argument or from a known uri (the argument
        `source` is for testing).
        Returns True if the description data are valid, otherwise
        returns False.
        """
        # compare the loaded identification with the separate
        # loaded box-information. The cache is valid if both are the same.
        boxinfo = self.get_boxinfo(source=source)
        return boxinfo.ident == self.descriptions[TR64_DEVICE].ident

    def _get_cache_path(self, create_cache_dir=True) -> pathlib.Path:
        """
        Returns a Path object for the cache-file. If cache_directory is
        not defined, the directory defaults to `~/.fritzconnection`.
        The filename gets constructed from the device-ip.
        The `create_cache_dir` argument is used for testing.
        """
        filename = self.ip_address.replace(".", "_")
        cache_filename = filename + FRITZ_CACHE_EXT
        if self.cache_directory:
            path = pathlib.Path(self.cache_directory)
        else:
            path = pathlib.Path().home() / FRITZ_CACHE_DIR
        if create_cache_dir:
            path.mkdir(exist_ok=True)
        return (path / cache_filename).resolve()
