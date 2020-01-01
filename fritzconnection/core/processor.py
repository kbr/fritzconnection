"""
Module to parse and store the device description and the service data
provided by xml and the scpd protocol based on xml. Names partly violate
PEP8 representing node-names from xml description files.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


from .utils import (
    get_xml_root,
    localname,
)


# ---------------------------------------------------------
# processor, decorator and descriptors here:
# ---------------------------------------------------------

def process_node(obj, root):
    """
    Take an object and a root of nodes. The node.text of nodes with the
    same name as an instance-attribute of 'obj' are set as values for
    the corresponding instance-attribute. If the attribute is a
    callable, processing the node gets delegated to the callable (which
    in turn calls process_node).
    """
    for node in root:
        node_name = localname(node)
        try:
            attr = getattr(obj, node_name)
        except AttributeError:
            # ignore unknown nodes
            continue
        if callable(attr):
            # attribute is a callable: delegate further
            attr(node)
        else:
            # node is an attribute: set value
            if isinstance(node.text, str):
                value = node.text.strip()
            else:
                value = node.text
            setattr(obj, node_name, value)


def processor(cls):
    """
    Class decorator to add the functionality of calling 'process_node'
    on invoking an instance as a callable.
    """
    cls.__call__ = lambda obj, root: process_node(obj, root)
    return cls


class ValueSequencer:
    """
    Data descriptor storing a value (assigned as attribute value) in a
    given sequence.
    """
    def __init__(self, sequence_name):
        self.sequence_name = sequence_name

    def __get__(self, obj, objtype):
        # kind of set only attribute
        return NotImplemented

    def __set__(self, obj, value):
        sequence = getattr(obj, self.sequence_name)
        sequence.append(value)


class InstanceAttributeFactory:
    """
    Non data descriptor returning instances of 'cls' and registering
    these instances in the '_storage' attribute of the calling instance.
    """
    def __init__(self, cls):
        self.cls = cls

    def __get__(self, obj, objtype):
        instance = self.cls()
        obj._storage.append(instance)
        return instance


class Storage:
    """
    Baseclass for classes working with InstanceAttributeFactory.
    """
    def __init__(self, storage):
        self._storage = storage


# ---------------------------------------------------------
# Node- and root-classes. Root classes are entry-points.
# Root classes are Scpd and Description.
# Description is the only public class.
# ---------------------------------------------------------

@processor
class SpecVersion:
    """
    Specification version from the schema device or service
    informations.
    """
    def __init__(self):
        # attributes are case sensitive node names:
        self.major = None
        self.minor = None

    @property
    def version(self):
        return f'{self.major}.{self.minor}'


@processor
class SystemVersion:
    """
    Information about the Fritz!OS version of the Fritz!Box.
    Information is just provided by the 'tr64desc.xml' file.
    """
    def __init__(self):
        # attributes are case sensitive node names
        self.HW = None
        self.Major = None
        self.Minor = None
        self.Patch = None
        self.Buildnumber = None
        self.Display = None

    @property
    def version(self):
        """
        Returns system version as string like '7.10' or None if system
        version is unknown.
        """
        if self.Minor and self.Patch:
            return f'{self.Minor}.{self.Patch}'
        return None


@processor
class Argument:
    """
    An argument with name, direction and relatedStateVariable
    attributes.
    """
    def __init__(self):
        # attributes are case sensitive node names
        self.name = None
        self.direction = None
        self.relatedStateVariable = None


@processor
class ArgumentList(Storage):
    """
    Collects the arguments for an action.
    """
    # case sensitive node
    argument = InstanceAttributeFactory(Argument)


@processor
class Action:
    """
    Every Action has a name and a list of arguments.
    """
    def __init__(self):
        self._arguments = list()
        self._arguments_storage = None
        # attributes are case sensitive node names:
        self.name = None
        self.argumentList = ArgumentList(self._arguments)

    @property
    def arguments(self):
        """
        Returns the action-arguments as a dict. argument-names are the
        keys and the argument objects are the values. The dictionary
        gets cached.
        """
        if not self._arguments_storage:
            self._arguments_storage = {arg.name: arg for arg in self._arguments}
        return self._arguments_storage


@processor
class ActionList(Storage):
    """
    Collection of actions of a service.
    The Action instances are stored in the Scpd.actions attribute.
    """
    # case sensitive node
    action = InstanceAttributeFactory(Action)


@processor
class ValueRange:

    def __init__(self):
        # attributes are case sensitive node names:
        self.minimum = None
        self.maximum = None
        self.step = None


@processor
class StateVariable:
    """
    Represents a stateVariable with the attributes name, dataType,
    defaultValue, allowedValueList and allowedValueRange.
    """
    # case sensitive node
    allowedValue = ValueSequencer('allowed_values')

    def __init__(self):
        # attributes are case sensitive node names:
        self.name = None
        self.dataType = None
        self.defaultValue = None
        self.allowed_values = list()
        self.allowedValueList = self
        self.allowedValueRange = ValueRange()


@processor
class ServiceStateTable(Storage):
    """
    Collection of stateVariables.
    """
    # case sensitive node
    stateVariable = InstanceAttributeFactory(StateVariable)


class Scpd:
    """
    Provides informations about the Service Control Point Definitions
    for every Service. Every Service has one instance of this class for
    accessing the description of it's own actions and the according
    parameters.
    Root class for processing the content of an scpd-file.
    """
    def __init__(self, root):
        """
        Starts interpreting the scpd-data. 'root' must be an xml.Element
        objects as returned from 'utils.get_xml_root'.
        """
        self._actions = list()
        self._state_variables = list()

        # attributes are case sensitive node names:
        self.specVersion = SpecVersion()
        self.actionList = ActionList(self._actions)
        self.serviceStateTable = ServiceStateTable(self._state_variables)

        # start node processing:
        process_node(self, root)

    @property
    def spec_version(self):
        return self.specVersion.version

    @property
    def actions(self):
        """
        Returns a dictionary with the actions from the actions-list. The
        action-names are the keys and the actions themself are the
        values.
        """
        return {action.name: action for action in self._actions}

    @property
    def state_variables(self):
        """
        Returns a dictionary with the state_variable name as keys and
        the StateVariable itself as value.
        """
        return {sv.name: sv for sv in self._state_variables}


@processor
class Service:
    """
    Class describing a service.
    """
    def __init__(self):
        self._scpd = None
        self._actions = None
        self._state_variables = None
        # attributes are case sensitive node names:
        self.serviceType = None
        self.serviceId = None
        self.controlURL = None
        self.eventSubURL = None
        self.SCPDURL = None

    @property
    def name(self):
        if self.serviceId:
            return self.serviceId.split(':')[-1]
        return None

    @property
    def actions(self):
        """
        Returns all known actions of this service as a dictionary.
        Action names are keys, the action objects are the values. Caches
        the dictionary once retrieved from _scpd.
        """
        if self._actions is None:
            self._actions = self._scpd.actions
        return self._actions

    @property
    def state_variables(self):
        """
        Returns all known stateVariables of this service as a
        dictionary. Names are keys, the stateVariables objects are the
        values. Caches the dictionary once retrieved from _scpd.
        """
        if self._state_variables is None:
            self._state_variables = self._scpd.state_variables
        return self._state_variables

    def load_scpd(self, address, port, timeout=None, session=None):
        """Loads the scpd data"""
        url = f'{address}:{port}{self.SCPDURL}'
        root = get_xml_root(url, timeout=timeout, session=session)
        self._scpd = Scpd(root)


@processor
class ServiceList(Storage):
    """
    Collection of Service instances for a device.
    The service instances are stored in the device.services attribute.
    """
    # case sensitive node
    service = InstanceAttributeFactory(Service)


@processor
class Device:
    """
    Storage for devices attributes and device subnodes.
    Subnodes are the serviceList and the deviceList.
    The services provided by a device are collected in services.
    Subdevices are collected in devices.
    All instance attributes are public for read only use.
    """
    def __init__(self):
        self._services = list()
        self.devices = list()
        # attributes are case sensitive node names:
        self.deviceType = None
        self.friendlyName = None
        self.manufacturer = None
        self.manufacturerURL = None
        self.modelDescription = None
        self.modelName = None
        self.modelNumber = None
        self.modelURL = None
        self.UDN = None
        self.UPC = None
        self.presentationURL = None
        self.serviceList = ServiceList(self._services)
        self.deviceList = DeviceList(self.devices)

    @property
    def services(self):
        services = {service.name: service for service in self._services}
        for device in self.devices:
            services.update(device.services)
        return services


@processor
class DeviceList(Storage):
    """
    Collection of sub-devices of a device.
    The Device instances are stored in the device.devices attribute of
    the parent device.
    """
    # case sensitive node
    device = InstanceAttributeFactory(Device)


class Description:
    """
    Root class for a given description information as the content from
    the files igddesc.xml or tr64desc.xml.
    """
    def __init__(self, root):
        """
        Starts data-processing. 'root' must be an xml.Element object as
        returned from 'utils.get_xml_root'.
        """
        # attributes are case sensitive node names:
        self.device = Device()
        self.specVersion = SpecVersion()
        self.systemVersion = SystemVersion()

        # start node processing:
        process_node(self, root)

    @property
    def device_model_name(self):
        return self.device.modelName

    @property
    def spec_version(self):
        return self.specVersion.version

    @property
    def system_version(self):
        """
        Returns the system version of the Fritz!Box as a string like
        '7.10' or None. This information is only available by the
        'tr64desc.xml' file.
        """
        return self.systemVersion.version

    @property
    def system_buildnumber(self):
        """
        Returns the buildnumber or None. This information is only
        available by the 'tr64desc.xml' file.
        """
        return self.systemVersion.Buildnumber

    @property
    def system_display(self):
        """
        Returns the system display-string or None. This information is
        only available by the 'tr64desc.xml' file.
        """
        return self.systemVersion.Display

    @property
    def services(self):
        """
        Returns dictionary with the known services as values and the
        according service-names as keys.
        """
        return self.device.services
