"""
processor.py

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)

Names partly violate PEP8 representing node-names from xml description files.
"""

from .utils import localname


def process_node(obj, root):
    """
    Take an object and a root of nodes. Nodes with the same name as an
    instance-attribute of 'obj' are set as values for the corresponding
    instance-attribute. If the attribute is a callable, processing the
    node gets delegated to the callable (which in turn calls
    process_node).
    """
    for node in root:
        node_name = localname(node)
        try:
            attr = getattr(obj, node_name)
        except AttributeError:
            # ignore node
            continue
        if callable(attr):
            # delegate further processing to callable
            attr(node)
        else:
            # set attribute value
            setattr(obj, node_name, node.text.strip())


def processor(cls):
    """
    Class decorator to add the functionality of calling 'process_node'
    if a class instance gets invoked as a callable.
    """
    cls.__call__ = lambda obj, root: process_node(obj, root)
    return cls


@processor
class SpecVersion:
    """
    Specification version from the schema device or service
    informations.
    """
    def __init__(self):
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
        self.name = None
        self.direction = None
        self.relatedStateVariable = None


@processor
class ArgumentList:

    def __init__(self, arguments):
        self._arguments = arguments

    @property
    def argument(self):
        argument = Argument()
        self._arguments.append(argument)
        return argument


@processor
class Action:
    """
    Every Action has a name and a list of arguments.
    """
    def __init__(self):
        self.name = None
        self._arguments = list()
        self._arguments_storage = None
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
class ActionList:
    """
    Collection of actions of a service.
    The Action instances are stored in the Scpd.actions attribute.
    """
    def __init__(self, actions):
        self.actions = actions

    @property
    def action(self):
        action = Action()
        self.actions.append(action)
        return action


class ValueSequencer:
    """
    Descriptor storing a value set as attribute in a given sequence.
    """
    def __init__(self, sequence_name):
        self.sequence_name = sequence_name

    def __get__(self, obj, objtype):
        # kind of set only attribute
        return NotImplemented

    def __set__(self, obj, value):
        sequence = getattr(obj, self.sequence_name)
        sequence.append(value)


@processor
class ValueRange:

    def __init__(self):
        self.minimum = None
        self.maximum = None
        self.step = None


@processor
class StateVariable:
    """
    Represents a stateVariable with the attributes name, dataType,
    defaultValue, allowedValueList and allowedValueRange.
    """
    allowedValue = ValueSequencer('allowed_values')

    def __init__(self):
        self.name = None
        self.dataType = None
        self.defaultValue = None
        self.allowed_values = list()
        self.allowedValueList = self
        self.allowedValueRange = ValueRange()


@processor
class ServiceStateTable:
    """
    Collection of stateVariables.
    """
    def __init__(self, state_variables):
        self._state_variables = state_variables

    @property
    def stateVariable(self):
        state_variable = StateVariable()
        self._state_variables.append(state_variable)
        return state_variable


@processor
class Scpd:
    """
    Provides informations about the Service Control Point Definitions
    for every Service. Every Service has one instance of this class for
    accessing the description of it's own actions and the according
    parameters.
    """
    def __init__(self):
        self._actions = list()
        self._state_variables = list()

        self.specVersion = SpecVersion()
        self.actionList = ActionList(self._actions)
        self.serviceStateTable = ServiceStateTable(self._state_variables)


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


@processor
class ServiceList:
    """
    Collection of Service instances for a device.
    The service instances are stored in the device.services attribute.
    """
    def __init__(self, services):
        # services is a reference to the parent device services attribute.
        self._services = services

    @property
    def service(self):
        """
        Internal property. Creates a new Service instance, stores this
        in the services attribute of the parent-device and returns the
        instance.
        """
        service = Service()
        self._services.append(service)
        return service


@processor
class DeviceList:
    """
    Collection of sub-devices of a device.
    The Device instances are stored in the device.devices attribute of
    the parent device.
    """
    def __init__(self, devices):
        # devices is a reference to the parent device devices attribute.
        self._devices = devices

    @property
    def device(self):
        """
        Internal property. Creates a new Device instance, stores this
        in the devices attribute of the parent-device and returns the
        instance.
        """
        device = Device()
        self._devices.append(device)
        return device


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
        self.deviceType = None
        self.friendlyName = None
        self.manufacturer = None
        self.manufacturerURL = None
        self.modelDescription = None
        self.modelName = None
        self.modelNumber = None
        self.modelURL = None
        self.UDN = None
        self.presentationURL = None
        self._services = list()
        self.devices = list()
        self.serviceList = ServiceList(self._services)
        self.deviceList = DeviceList(self.devices)

    @property
    def services(self):
        services = {service.name: service for service in self._services}
        for device in self.devices:
            services.update(device.services)
        return services


class Description:
    """
    Root class for a given description information as the content from
    the files igddesc.xml or tr64desc.xml.
    Public api given by the corresponding marked properties.
    """
    def __init__(self, root):
        self.device = Device()
        self.specVersion = SpecVersion()
        self.systemVersion = SystemVersion()
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
    def services(self):
        """
        Returns dictionary with the known services as values and the
        according service-names as keys.
        """
        return self.device.services
