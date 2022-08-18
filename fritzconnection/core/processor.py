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
# Processors for reading the device specific FritzOS api:
# Node- and root-classes. Root classes are entry-points.
# Root classes are Scpd and Description.
# Description is the only public class.
# ---------------------------------------------------------


class Serializer:
    """
    Simple abstract Serializer base class.
    This class and should not get instanciated.
    """

    def __eq__(self, other):
        if set(self.__dict__.keys()) ^ set(other.__dict__.keys()):
            # self and other have not the same set of instance attributes:
            return False
        # both instances must have all the same attribute values:
        return self._compare_attributes(other, self.__dict__.keys())

    def _compare_attributes(self, other, attributes):
        # check for the same values in the attributes of self and other:
        for attribute in attributes:
            if getattr(self, attribute) != getattr(other, attribute):
                return False
        return True

    def serialize(self, exclude=None):
        if exclude is None:
            exclude = []
        attribute_names = set(self.__dict__.keys()) - set(exclude)
        return self.get_sorted_dict(
            {name: getattr(self, name) for name in attribute_names}
        )

    def deserialize(self, data):
        self.__dict__.update(data)

    @staticmethod
    def get_sorted_dict(dictionary):
        """
        Takes a dictionary and returns another one with all keys in
        alphabetical order.
        """
        sorted_keys = sorted(dictionary.keys())
        return {key: dictionary[key] for key in sorted_keys}

    @classmethod
    def from_data(cls, data):
        """
        Return a new instance with attributes initialized from data.
        """
        try:
            instance = cls()
        except TypeError:
            # will happen on classes expecting a list of nodes:
            instance = cls(root=[])
        instance.deserialize(data)
        return instance


@processor
class SpecVersion(Serializer):
    """
    Specification version from the schema device or service
    information.
    """
    def __init__(self):
        # attributes are case sensitive node names:
        self.major = None
        self.minor = None

    @property
    def version(self):
        return f'{self.major}.{self.minor}'


@processor
class SystemVersion(Serializer):
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

    @property
    def info(self):
        """
        Returns a tuple with all instance attributes 'HW, Major, Minor,
        Patch, Buildnumber, Display' in this order.
        """
        return (
            self.HW,
            self.Major,
            self.Minor,
            self.Patch,
            self.Buildnumber,
            self.Display,
        )


@processor
class Argument(Serializer):
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
class Action(Serializer):
    """
    Every Action has a name and a list of arguments.
    """
    def __init__(self):
        self._arguments = list()
        self._arguments_storage = None
        # attributes are case sensitive node names:
        self.name = None
        self.argumentList = ArgumentList(self._arguments)

    def __eq__(self, other):
        # for testing: Action is equal to another if the name is the same
        # and the arguments in self._arguments are the same and in the
        # same order (because of the implementation).
        if self.name == other.name:
            for arg1, arg2 in zip(self._arguments, other._arguments):
                if arg1 != arg2:
                    return False
            return True
        return False

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

    def serialize(self):
        """
        Return a dictionary with json serializable data: the name of the
        instance and a list of the serialized argument-instances in
        self._arguments.
        """
        exclude = ["_arguments", "_arguments_storage", "argumentList"]
        data = super().serialize(exclude=exclude)
        data['arguments'] = [arg.serialize() for arg in self._arguments]
        return data

    def deserialize(self, data):
        """
        Deserialize the data back to an Action instance with a given
        name and defined Argument-instances.
        """
        self.name = data['name']
        self._arguments = [Argument.from_data(d) for d in data['arguments']]


@processor
class ActionList(Storage):
    """
    Collection of actions of a service.
    The Action instances are stored in the Scpd.actions attribute.
    """
    # case sensitive node
    action = InstanceAttributeFactory(Action)


@processor
class ValueRange(Serializer):

    def __init__(self):
        # attributes are case sensitive node names:
        self.minimum = None
        self.maximum = None
        self.step = None


@processor
class StateVariable(Serializer):
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
        self.allowed_values = list()  # list of values as strings
        self.allowedValueList = self
        self.allowedValueRange = ValueRange()

    def __eq__(self, other):
        # two instances are equal on having the same attribute values.
        attributes = ["name", "dataType", "defaultValue", "allowed_values"]
        if not self._compare_attributes(other, attributes):
            return False
        return self.allowedValueRange == other.allowedValueRange

    def serialize(self):
        """
        Returns a dictionary with json serializable attribute data.
        """
        exclude = ["allowedValueList", "allowedValueRange"]
        data = {"attributes": super().serialize(exclude=exclude)}
        data["allowedValueRange"] = self.allowedValueRange.serialize()
        return data

    def deserialize(self, data):
        """
        Deserialize the data back to a former state of a StateVariable
        instance.
        """
        super().deserialize(data['attributes'])
        self.allowedValueRange.deserialize(data['allowedValueRange'])


@processor
class ServiceStateTable(Storage):
    """
    Collection of stateVariables.
    """
    # case sensitive node
    stateVariable = InstanceAttributeFactory(StateVariable)


class Scpd(Serializer):
    """
    Provides information about the Service Control Point Definitions
    for every Service. Every Service has one instance of this class for
    accessing the description of its own actions and the according
    parameters.
    Root class for processing the content of an scpd-file.
    """
    def __init__(self, root):
        """
        Starts interpreting the scpd-data. 'root' must be a xml.Element
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

    def __eq__(self, other):
        attributes = ["_actions", "_state_variables", "specVersion"]
        return self._compare_attributes(other, attributes)

    @property
    def spec_version(self):
        return self.specVersion.version

    @property
    def actions(self):
        """
        Returns a dictionary with the actions from the actions-list. The
        action-names are the keys and the actions themselves are the
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

    def serialize(self):
        data = {"actions": [action.serialize() for action in self._actions]}
        data['state_variables'] = [sv.serialize() for sv in self._state_variables]
        data['specVersion'] = self.specVersion.serialize()
        return self.get_sorted_dict(data)

    def deserialize(self, data):
        self._actions = [Action.from_data(d) for d in data['actions']]
        self._state_variables = [StateVariable.from_data(d) for d in data['state_variables']]
        self.specVersion.deserialize(data['specVersion'])


@processor
class Service(Serializer):
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

    def serialize(self):
        """
        Serialize the service instance attributes. Returns a dictionary
        with data that can be converted to json.
        """
        exclude = ['_scpd', '_actions', '_state_variables']
        return {
            "attributes": super().serialize(exclude=exclude),
            "scpd": self._scpd.serialize()
        }

    def deserialize(self, data):
        """
        Inverse method for `serialize`. Takes the data (a dictionary)
        and populates the instance attributes extracted by `serialize`.
        """
        super().deserialize(data['attributes'])
        self._scpd = Scpd.from_data(data['scpd'])


@processor
class ServiceList(Storage):
    """
    Collection of Service instances for a device.
    The service instances are stored in the device.services attribute.
    """
    # case sensitive node
    service = InstanceAttributeFactory(Service)


@processor
class Device(Serializer):
    """
    Storage for devices attributes and device sub-nodes.
    Sub-nodes are the serviceList and the deviceList.
    The services provided by a device are collected in services.
    Sub-devices are collected in devices.
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

    def __eq__(self, other):
        attributes = [
            "deviceType", "friendlyName", "manufacturer", "manufacturerURL",
            "modelDescription", "modelName", "modelNumber", "modelURL",
            "UDN", "UPC", "presentationURL",
        ]
        return self._compare_attributes(other, attributes)

    @property
    def services(self):
        services = {service.name: service for service in self._services}
        for device in self.devices:
            services.update(device.services)
        return services

    def serialize(self):
        """
        Returns a dictionary with a subset of the instance attributes
        and a list of serialized services that can be transformed to
        json-format.
        """
        exclude = ["_services", "devices", "serviceList", "deviceList",]
        data = {'attributes': super().serialize(exclude=exclude)}
        data['services'] = [service.serialize() for service in self._services]
        data['devices'] = [device.serialize() for device in self.devices]
        return self.get_sorted_dict(data)

    def deserialize(self, data):
        """
        Loads the data into the instance attributes. This is the
        reverse-function for serialize. No return value.
        """
        super().deserialize(data['attributes'])
        self._services.extend([Service.from_data(d) for d in data['services']])
        self.devices.extend([Device.from_data(d) for d in data['devices']])


@processor
class DeviceList(Storage):
    """
    Collection of sub-devices of a device.
    The Device instances are stored in the device.devices attribute of
    the parent device.
    """
    # case sensitive node
    device = InstanceAttributeFactory(Device)


class Description(Serializer):
    """
    Root class for a given description information as the content from
    the files igddesc.xml or tr64desc.xml.
    """
    def __init__(self, root):
        """
        Starts data-processing. 'root' must be a xml.Element object as
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
    def system_info(self):
        """
        Returns the systemVersion attributes as a tuple:
        (HW, Major, Minor, Patch, Buildnumber, Display). This information
        is only available by the 'tr64desc.xml' file.
        """
        return self.systemVersion.info

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

    def serialize(self):
        """
        Return serialized instance attributes as dictionary.
        """
        return {
            'device': self.device.serialize(),
            'specVersion': self.specVersion.serialize(),
            'systemVersion': self.systemVersion.serialize(),
        }

    def deserialize(self, data):
        """
        Sets the instance attributes according to data.
        """
        self.device.deserialize(data['device'])
        self.specVersion.deserialize(data['specVersion'])
        self.systemVersion.deserialize(data['systemVersion'])


# ---------------------------------------------------------
# Processors to interpret the information returned from
# the "X_AVM-DE_GetHostListPath" action.
# ---------------------------------------------------------

@processor
class Host:
    """
    Host class providing every requested attribute
    """
    _int_values = {'Index', 'X_AVM-DE_Port', 'X_AVM-DE_Speed'}
    _bool_values = {
        'Active',
        'X_AVM-DE_UpdateAvailable',
        'X_AVM-DE_Guest', 'X_AVM-DE_VPN',
        'X_AVM-DE_Disallow',
    }

    def __getattr__(self, attr_name):
        # do the magic of not raising an AttributeError:
        setattr(self, attr_name, None)
        return getattr(self, attr_name)

    @property
    def attributes(self):
        """
        Provide all attributes of the instance as a dictionary with the
        attribute names as keys and the values converted to python
        datatypes.
        """
        attrs = {}
        for name, value in self.__dict__.items():
            if name in self._int_values:
                attrs[name] = int(value)
            elif name in self._bool_values:
                attrs[name] = bool(int(value))
            else:
                attrs[name] = value
        return attrs


@processor
class HostStorage(Storage):
    """
    Storage class collection all Item-nodes describing the hosts.
    The Item-nodes are converted to _Host instances.
    """
    Item = InstanceAttributeFactory(Host)  # 'Item' must match node-name

    def __init__(self, root):
        self._hosts = list()
        super().__init__(self._hosts)
        self(root)  # start process_node()

    @property
    def hosts_attributes(self):
        """
        Provide a list of dictionaries with the attributes of all hosts.
        The list is sorted with the lowest Index number first.
        """
        # list is already sorted from FritzOS,
        # but don't trust this for any time in the future.
        return sorted(
            [host.attributes for host in self._hosts],
            key = lambda attrs: attrs["Index"]
        )
