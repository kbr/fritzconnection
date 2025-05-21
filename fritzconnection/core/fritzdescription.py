"""
Loads the description files from the device describing the API. A device
can be a router or a repeater.
"""

from fritzconnection.core.description import TR64Description
from fritzconnection.core.description import UPnPInternetGatewayDescription
from fritzconnection.core.exceptions import FritzResourceError
from fritzconnection.core.utils import get_xml_root


FRITZ_IGD_DESC_FILE = "igddesc.xml"
FRITZ_TR64_DESC_FILE = "tr64desc.xml"
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

    def __init__(self, ip_address=None, uri=None, session=None, use_cache=True):
        self.descriptions = {
            IGD_DEVICE: UPnPInternetGatewayDescription(),
            TR64_DEVICE: TR64Description()
        }
        self.ip_address = ip_address
        self.uri = uri
        self.session = session
        self.use_cache = use_cache
        self._services = {}

    @property
    def services(self):
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

    @property
    def system_version(self):
        return self.descriptions[TR64_DEVICE].system_version

    def load_descriptions(self):
        if self.use_cache:
            self.load_descriptions_from_cache()
        else:
            self.load_descriptions_from_device()

    def load_descriptions_from_cache(self):
        # not implemented, so same behaviour as for an invalide cache:
        self.load_descriptions_from_device()

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
        if igd_source:
            try:
                root = get_xml_root(igd_source)
            except FritzResourceError:
                # can happen if the device does not support
                # an igd_file (i.e. it is not a WAN device)
                pass
            else:
                self.descriptions[IGD_DEVICE].load(root)
        if tr64_source:
            # it is an error if this source is not available
            root = get_xml_root(tr64_source)
            self.descriptions[TR64_DEVICE].load(root)
