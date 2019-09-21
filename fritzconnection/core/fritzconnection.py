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


class ServiceError(FritzConnectionException):
    """Exception raised by calling nonexisting services."""


# ---------------------------------------------------------
# Nodes and Components
# name conventions adapted from the description files
# ---------------------------------------------------------

class AbstractDescriptionNode:
    """
    Abstract class for scanning all childs of a given node and storing
    the according information as instance attributes: the tag-names are
    the attribute names and the content (node.text) is stored as the
    value.
    """

    sequences = {}
    tag_attributes = {}

    def __init__(self, root):
        super().__init__()
        for name in self.sequences:
            setattr(self, name, list())
        self.tag_attributes.update(root.attrib)
        for node in root:
            self.process_node(node)

    def process_node(self, node):
        """
        Default node processing: if node-name in self.sequences then it
        is a child-node with subnodes
        """
        name = self.node_name(node)
        if name in self.sequences:
            sequence = getattr(self, name)
            sequence.append(self.sequences[name](node))
        else:
            try:
                setattr(self, name, node.text.strip())
            except TypeError:
                # can happen on none-text nodes like comments
                # ignore this
                pass

    @staticmethod
    def node_name(node):
        """
        Strips the namespace from the node-tag and returns this as
        node-name.
        """
        if isinstance(node.tag, str):
            return node.tag.split('}')[-1]
        return node.tag


class SpecVersion(AbstractDescriptionNode):
    """
    Specification version node holding the description file
    specification version from the schema device or service
    informations.
    """

    @property
    def version(self):
        return f'{self.major}.{self.minor}'


# scpd-section ----------------------------------

class AllowedValueList(AbstractDescriptionNode):
    """stores a list of allowed values."""

    sequences = {'values': None}

    def process_node(self, node):
        """
        node can be a repeated allowedValue tag without subnodes.
        Therefor the tag.text has to be collected here.
        """
        self.values.append(node.text.strip())


class AllowedValueRange(AbstractDescriptionNode):
    """stores attributes of an allowed range"""


class StateVariable(AbstractDescriptionNode):
    """
    collects 'name', 'datatype' and 'defaultValue' or 'allowedValueList'
    of action parameter data.
    """

    sequences = {
        'allowedValueList': AllowedValueList,
        'allowedValueRange': AllowedValueRange,
    }

    @property
    def type(self):
        """convenient access to dataType."""
        return self.dataType

    @property
    def default(self):
        """Returns the default-value or None."""
        try:
            return self.defaultValue
        except AttributeError:
            return None

    @property
    def allowed_values(self):
        """
        Returns a list of allowed values. Returns an empty list if there
        are no allowed values.
        """
        return self.allowedValueList

    @property
    def allowed_value_range(self):
        """
        Returns a dictionary with informations about the allowed value
        range. Keys can be 'minimum', 'maximum' and 'step', depending on
        the stateVariable.
        """
        try:
            return self.allowedValueRange[0].__dict__
        except IndexError:
            return None


class Argument(AbstractDescriptionNode):
    """
    Collects 'name' and 'direction' of the argument. Also the
    'relatedStateVariable' which is the name of a StateVariable instance
    describing the type of the argument.
    """

    @property
    def state_variable_name(self):
        """more pythonic name for 'relatedStateVariable'."""
        return self.relatedStateVariable


class ArgumentList(AbstractDescriptionNode):
    """list of Arguments. No more instance attributes."""

    sequences = {'argument': Argument}

    def __len__(self):
        return len(self.argument)

    def __iter__(self):
        return iter(self.argument)


class Action(AbstractDescriptionNode):
    """
    Action class with 'name' and 'argumentList'. Arguments are optional,
    so the 'argumentList' can be empty.

    An Action also has direct access to its 'arguments'. This is a
    dictionary with the argument names as keys and the Argument
    instances as values.
    """

    sequences = {'argumentList': ArgumentList}
    arguments = {}

    def __init__(self, root):
        super().__init__(root)
        if self.argumentList:
            self.arguments = {
                argument.name: argument for argument in self.argumentList[0]
            }



# desc-section ----------------------------------

class Service(AbstractDescriptionNode):
    """
    Service node holding all informations about a service as instance
    attributes, i.e.:

    'SCPDURL': '/igddslSCPD.xml',
    'controlURL': '/igdupnp/control/WANDSLLinkC1',
    'eventSubURL': '/igdupnp/control/WANDSLLinkC1',
    'serviceId': 'urn:upnp-org:serviceId:WANDSLLinkC1',
    'serviceType': 'urn:schemas-upnp-org:service:WANDSLLinkConfig:1'

    The service.name is the last part of the attribute 'serviceID', i.e.
    'WANDSLLinkC1'

    """

    @property
    def name(self):
        return self.serviceId.split(':')[-1]


class ServiceList(AbstractDescriptionNode):
    """Collection of Service objects."""

    sequences = {'service': Service}

    def __len__(self):
        return len(self.service)

    def __iter__(self):
        return iter(self.service)


class Device(AbstractDescriptionNode):
    """
    A router device for a collection of services. Can also have a
    collection of sub-devices.
    """

    sequences = {'serviceList': ServiceList, 'deviceList': None}

    @property
    def services(self):
        if self.serviceList:
            return self.serviceList[0]
        return self.serviceList

    @property
    def devices(self):
        if self.deviceList:
            return self.deviceList[0]
        return self.deviceList

    @property
    def modelname(self):
        return self.modelName

    def collect_services(self):
        """
        Returns a dictionary with the services of this device and
        all nested devices. The keys are the servicenames and the
        service instances are the values.
        """
        services = {service.name: service for service in self.services}
        for device in self.devices:
            services.update(device.collect_services())
        return services


class DeviceList(AbstractDescriptionNode):
    """Collection of Device objects."""

    sequences = {'device': Device}

    def __len__(self):
        return len(self.device)

    def __iter__(self):
        return iter(self.device)

Device.sequences['deviceList'] = DeviceList


class Description(AbstractDescriptionNode):
    """
    Root class for a given description information like igddesc.xml or
    tr64desc.xml

    Instances have the attributes:

    - device: Device instance of the root device
    - specVersion: for a SpecVersion instance
    - specification: for easy access of the SpecVersion version
    - presentation_url: to access the box (http://fritz.box)
    - namespace: xmlns value from the root node
    """

    sequences = {'specVersion': SpecVersion, 'device': Device}

    def __init__(self, root):
        self.namespace = etree.QName(root.tag).namespace
        super().__init__(root)

    @property
    def specification(self):
        return self.specVersion[0].version

    @property
    def modelname(self):
        return self.device[0].modelname

    def collect_services(self):
        """
        Returns a dictionary with the services of the root-device and
        all nested devices. The keys are the servicenames and the
        service instances are the values.
        """
        services = {}
        for device in self.device:
            services.update(device.collect_services())
        return services


# ---------------------------------------------------------
# ServiceManager:
# separate class for better testing
# ---------------------------------------------------------

class ServiceManager:
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


