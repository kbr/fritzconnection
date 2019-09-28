"""
Nodes for desc- and scpd-informations.
"""

from lxml import etree


# ---------------------------------------------------------
# decorator instead of a metaclass
# ---------------------------------------------------------

def sequencer(sequence_name):
    """
    Class decorator extending a list node to an object that has a length
    and is iterable. 'sequence_name' is the name of the list-like
    attribute.
    """

    def _sequencer(cls):
        cls.__len__ = lambda self: len(getattr(self, sequence_name))
        cls.__iter__ = lambda self: iter(getattr(self, sequence_name))
        return cls

    return _sequencer


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
        is a child-node with subnodes.
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
        Strips the namespace from the node-tag and returns the remaining
        part as node-name.
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


class Service(AbstractDescriptionNode):
    """
    Storage for service attributes, like:
    serviceType: urn:schemas-upnp-org:service:WANIPConnection:1
    serviceId: urn:upnp-org:serviceId:WANIPConn1
    controlURL: /igdupnp/control/WANIPConn1
    eventSubURL: /igdupnp/control/WANIPConn1
    SCPDURL: /igdconnSCPD.xml
    """

    scpd = None

    @property
    def name(self):
        return self.serviceId.split(':')[-1]

    @property
    def actions(self):
        pass


@sequencer('service')
class ServiceList(AbstractDescriptionNode):
    """Storage for Service objects"""

    sequences = {'service': Service}


class Device(AbstractDescriptionNode):
    """
    Storage for devices attributes:
    deviceType: urn:schemas-upnp-org:device:InternetGatewayDevice:1
    friendlyName: FRITZ!Box 7590
    manufacturer: AVM Berlin
    manufacturerURL: http://www.avm.de
    modelDescription: FRITZ!Box 7590
    modelName: FRITZ!Box 7590
    modelNumber: avm
    modelURL: http://www.avm.de
    UDN: uuid:<a unique id here>

    Stores also Services in the serviceList and sub-devices in the
    deviceList. deviceList is a forward declaration not known by Python.
    """

    sequences = {'serviceList': ServiceList, 'deviceList': None}

    @property
    def uuid(self):
        return self.UDN.split(':', 1)[-1]

    @property
    def model_name(self):
        return self.modelName

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

    def collect_services(self):
        """
        Returns a dictionary of the services in serviceList. Service
        names are the keys, the service objects are the values.
        """
        services = {service.name: service for service in self.services}
        for device in self.devices:
            services.update(device.collect_services())
        return services


@sequencer('device')
class DeviceList(AbstractDescriptionNode):
    """Collection of Device objects."""

    sequences = {'device': Device}

# backward declaration/injection of the deviceList
Device.sequences['deviceList'] = DeviceList


class Description(AbstractDescriptionNode):
    """
    Root class for a given description information like igddesc.xml or
    tr64desc.xml

    Instances have the attributes:

    - root_device: Device instance of the root device
    - specVersion: for a SpecVersion instance
    - specification: for easy access of the SpecVersion version
    - presentation_url: to access the box (http://fritz.box)
    - namespace: xmlns value from the root node

    All available services are collected in the 'services' attribute
    which is a dictionary with the service names as keys and the service
    objects as values.
    """

    sequences = {'specVersion': SpecVersion, 'device': Device}

    def __init__(self, root):
        self.namespace = etree.QName(root.tag).namespace
        super().__init__(root)
        self.root_device = self.device[0]
        self.services = self.root_device.collect_services()

    @property
    def spec_version(self):
        return self.specVersion[0].version

    @property
    def device_model_name(self):
        return self.root_device.model_name


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
    """
    Stores attributes of an allowed range like
    'minimum', 'maximum', 'step'
    """


class StateVariable(AbstractDescriptionNode):
    """
    collects 'name', 'dataType' and 'defaultValue' or 'allowedValueList'
    of action parameter data.
    A StateVariable instance also known its tag_attributes, which is a dictionary: i.e. given the tag <stateVariable sendEvents="no"> then the value "no" can accessed by:

    >>> sv = StateVariable(root)
    >>> sv.tag_attributes['sendEvents']
    'no'

    """

    sequences = {
        'allowedValueList': AllowedValueList,
        'allowedValueRange': AllowedValueRange,
    }


@sequencer('stateVariable')
class ServiceStateTable(AbstractDescriptionNode):
    """
    Collection of StateVariables. Is iterable and can access the
    StateVariables by name by the dict 'self.state_variables'.
    """

    sequences = {'stateVariable': StateVariable}

    def __init__(self, root):
        super().__init__(root)
        self.state_variables = {
            sv.name: sv for sv in self.stateVariable
        }


class Argument(AbstractDescriptionNode):
    """
    Container class for the attributes:
    'name', 'direction', 'relatedStateVariable'
    """


@sequencer('argument')
class ArgumentList(AbstractDescriptionNode):
    """Sequence of Arguments."""

    sequences = {'argument': Argument}


class Action(AbstractDescriptionNode):
    """
    Class representing an Action with a 'name' and an ArgumentList. The
    Argument objects can be accessed by name via the 'self.arguments'
    dictionary.
    """

    sequences = {'argumentList': ArgumentList}
    arguments = {}

    def __init__(self, root):
        super().__init__(root)
        if self.argumentList:
            self.arguments = {
                arg.name: arg for arg in self.argumentList[0]
            }


@sequencer('action')
class ActionList(AbstractDescriptionNode):
    """Sequence of Actions."""

    sequences = {'action': Action}


class Scpd(AbstractDescriptionNode):
    """
    Service description object, specific for every service. Hold the
    namespace, specVersion and an actionList with all available Actions.
    The Actions can also be accessed by name by the 'actions' attribute
    (which is a dictionary).
    """

    sequences = {'specVersion': SpecVersion, 'actionList': ActionList}
    actions = {}

    def __init__(self, root):
        self.namespace = etree.QName(root.tag).namespace
        super().__init__(root)
        if self.actionList:
            self.actions = {
                action.name: action for action in self.actionList[0]
            }

    @property
    def spec_version(self):
        return self.specVersion[0].version
