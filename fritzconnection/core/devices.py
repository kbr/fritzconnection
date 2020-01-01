"""
Implements the DeviceManager for physical and virtual devices. Every
physical device (a router) has a set of virtual subdevices.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


from .processor import Description
from .utils import get_xml_root


class DeviceManager:
    """
    Knows all data about the device and the subdevices, including the
    available services. Takes an optional `timeout` parameter to limit
    the time waiting for a router response. The optional parameter
    `session` is a reusable connection and can speed up the
    communication with the device. In case `session` is given, `timeout`
    will not get used.
    """

    def __init__(self, timeout=None, session=None):
        self.descriptions = []
        self.services = {}
        self.timeout = timeout
        self.session = session

    @property
    def modelname(self):
        """
        Take the root-device of the first description and return the
        according modelname. This is the name of the Fritz!Box itself.
        Will raise an IndexError if the method is called before
        descriptions are added.
        """
        return self.descriptions[0].device_model_name

    @property
    def system_version(self):
        """
        Returns a tuple with version, display and buildnumber from the
        first description providing this informations. Returns None if
        no system informations are available.
        """
        version = None
        for description in self.descriptions:
            version = description.system_version
            if version:
                return version
        return None

    def add_description(self, source):
        """
        Adds description data about the devices and the according
        services. 'source' is a string with the xml-data, like the
        content of an igddesc- or tr64desc-file.
        """
        root = get_xml_root(source, timeout=self.timeout, session=self.session)
        self.descriptions.append(Description(root))

    def scan(self):
        """
        Scans all available services defined by the description files.
        Must get called after all xml-descriptions are added.
        """
        for description in self.descriptions:
            self.services.update(description.services)

    def load_service_descriptions(self, address, port):
        """
        Triggers the load of the scpd files of the services, so they
        known their actions.
        """
        for service in self.services.values():
            service.load_scpd(
                address, port, timeout=self.timeout, session=self.session
            )

