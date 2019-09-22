"""
fritzconnection 1.0
requires Python >= 3.6
"""


__version__ = '1.0_alpha_1'


import os
import string

import requests
from requests.auth import HTTPDigestAuth

from lxml import etree


# FritzConnection defaults:
FRITZ_IP_ADDRESS = '169.254.1.1'
FRITZ_TCP_PORT = 49000
FRITZ_IGD_DESC_FILE = 'igddesc.xml'
FRITZ_TR64_DESC_FILE = 'tr64desc.xml'
FRITZ_USERNAME = 'dslf-config'


def get_version():
    """returns the module version"""
    return __version__


# ---------------------------------------------------------
# fritzconnection specific exceptions:
# ---------------------------------------------------------

class FritzConnectionException(Exception):
    """Base Exception for communication errors with the Fritz!Box"""


class ActionError(FritzConnectionException):
    """Exception raised by calling nonexisting actions."""


class ServiceError(FritzConnectionException):
    """Exception raised by calling nonexisting services."""



# ---------------------------------------------------------
# ServiceManager:
# separate class for better testing
# ---------------------------------------------------------

class DeviceManager:
    """
    Knows all data about the device and the sub-devices, including the
    available services.
    """

    def __init__(self):
        self.descriptions = []
        self.services = {}

    def add_description(self, source):
        """
        Adds description data about the devices and the according
        services. 'source' is a string with the xml-data, like the
        content of an igddesc- or tr64desc-file.
        """
        tree = etree.parse(source)
        root = tree.getroot()
        self.descriptions.append(Description(root))

    def scan(self):
        """
        Scans all available services defined by the description files.
        Must get called after all xml-descriptions are added.
        """
        for description in self.descriptions:
            self.services.update(description.services)




class x_ServiceManager:
    """
    Class for accessing all services given by Description objects.

    Also the ServiceManager is an iterator for all Service objects.

    A Fritz!Box may provide more than one description file. Every file
    is represented by a Description object.
    """

    def __init__(self):
        self.descriptions = []
        self.services = {}


    @property
    def modelname(self):
        """
        Take the root-device of the first description and return the
        according modelname. This is the name of the Fritz!Box itself.
        Will raise an IndexError if the method is called before
        descriptions are added.
        """
        return self.descriptions[0].modelname

    def add_xml_description(self, source):
        """
        Expects the xml-source of a description file.
        'source' must be a file like object.
        Creates a new Description instance with this source and adds the
        instance to self.descriptions.
        """
        tree = etree.parse(source)
        root = tree.getroot()
        self.descriptions.append(Description(root))

    def scan(self):
        """
        Scans all available services defined by the description files.
        Must get called after all xml-descriptions are added.
        """
        for description in self.descriptions:
            self.services.update(description.collect_services())

    def get_service(self, name):
        """
        Returns a service instance with the given name or raises a
        ServiceError.
        """
        name = self.normalize_name(name)
        try:
            return self.services[name]
        except KeyError:
            message = f'unknown Service "{name}"'
            raise ServiceError(message)

    @staticmethod
    def normalize_name(name):
        """
        Servicenames are of the form '<name><digit>' like
        'WLANConfiguration1'. For backward-compatibility also the forms
        '<name>' without a digit and '<name>:<digit>' are allowed.
        In case of a missing digit a '1' will get appended to the name,
        in case of a colon the colon gets removed.
        """
        if ':' in name:
            name, number = name.split(':', 1)
            return name + number
        if name[-1] not in string.digits:
            return name + '1'
        return name


# ---------------------------------------------------------
# core class: FritzConnection
# ---------------------------------------------------------

class FritzConnection:

    def __init__(self, address=None, port=None, user=None, password=None,
                 fobj=None):
        """
        Initialisation of FritzConnection: reads all data from the box
        and also the api-description (the servicenames and according
        actionnames as well as the parameter-types) that can vary among
        models and stores these informations as instance-attributes.
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
        hardcoding.

        For testing only: 'fobj' is a file like object with description
        informations.

        """
        if address is None:
            address = FRITZ_IP_ADDRESS
        if port is None:
            port = FRITZ_TCP_PORT
        if user is None:
            user = os.getenv('FRITZ_USERNAME', FRITZ_USERNAME)
        if password is None:
            password = os.getenv('FRITZ_PASSWORD', '')

        self.address = address
        self.port = port
        self.user = user
        self.password = password
        self.service_manager = self._get_service_manager(fobj)

    def _get_service_manager(self, fobj):
        """
        Returns a ServiceManager instance with the Fritz!Box API
        descriptions and access methods.
        """
        service_manager = ServiceManager()
        if not fobj:
            sources = self._get_description_sources()
        elif isinstance(fobj, list):
            sources = fobj
        else:
            sources = [fobj]
        for source in sources:
            print(source)
            service_manager.add_xml_description(source)
        service_manager.scan()
        return service_manager

    def _get_description_sources(self):
        pass


