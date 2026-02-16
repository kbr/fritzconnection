"""
Definition of all description nodes as dataclasses with methods for
parsing.

The classes may have attibutes violating PEP 8 representing the original
typography in the xml-sources.


.. NOTE::
   this module should only implement classes used by the core-modules. Library modules should define description-classes inside the library.


Descriptive parsing of xml-structures
=====================================


This module defines helper functions to convert an xml-datastructure to
Python datastructure of nested classes with attributes:

* the decorator `@description`
* the mixin class `ListItemIteratorMixin`

The module also makes use of::

    >>> from dataclasses import field


Basic: a node with subnodes
---------------------------

Consider a simple xml-structure like::

    xml_source = '''\
    <User>
        <Name>Tim</Name>
        <location>Office</location>
    </User>
    '''

that can be read from a string or a file to an ElementTree structure::

    >>> from xml.etree import ElementTree as etree
    >>> root = etree.fromstring(xml_source)


Now the datastructure `User` can be represented by a Python class as the
root-node and class attributes with the same names as the sub-nodes
`Name` and `location` (case sensitivity matters). The `@description`
decorater convertes the class to a `dataclass` so the instance
attributes `Name` and `location` must be defined with type-annotations.
All type-annotations of leaf-nodes should be of type `str` with default
as an empty string:

    @description
    class User:
        Name: str = ""
        location: str = ""

    >>> user = User()
    >>> user.load(root)
    >>> user
    User(Name='Tim', location='Office', attrib={})
    
    
The `@description` decorator also adds a `load`-function to the `User`
class to read the xml-source and provides an additional attribute
`attrib` for storing attributes of the nodes. Consider a modified
xml-source with attributes for `User` and `location`:

    <User admin="True">
        <Name>Tim</Name>
        <location type="work">Office</location>
        <phone>123456</phone>
    </User>
    
    
The instance of `User` now holds the attribute in the `attrib` dictionary:
    
    >>> user = User()
    >>> user.load(root)
    >>> user
    User(Name='Tim', location='Office', attrib={'admin': 'True'})
    
    
The content of the subnodes are also accessible as attributes. The
subnodes are leaf-nodes of type string but with an addtional attribute
`attrib`:

    >>> user.Name
    'Tim'

    >>> user.Name.attrib
    {}

    >>> user.location
    'Office'
    
    >>> user.location.attrib
    {'type': 'work'}
    

Handling missing or undefined content:
--------------------------------------

Undefined or missing content is simply ignored. Consider that the
xml-source has more nodes than the Python description defines, i.e.
a phone-node:

    <User admin="True">
        <Name>Tim</Name>
        <location type="work">Office</location>
        <phone>123456</phone>
    </User>


Next consider the Python description defines an attribute `email` which
is not part of the xml-source:

    @description
    class User:
        Name: str = ""
        location: str = ""
        email: str = ""

    >>> user = User()
    >>> user.load(root)
    >>> user
    User(Name='Tim', location='Office', attrib={'admin': 'True'})


This will give the same datastructure as before: nodes given in the
xml-source, but not defined in the class-description, are ignored – and
attributes defined in the class description, but not represented by the
xml-source, will hold their default-values.


Handling sequences:
-------------------

Sequences are recuring subnodes, which are not leafs, i.e. multiple
`User` nodes as subnodes in a `Users` node. So consider a more nested
structure describing a set of users by a root-node `Users`:

    <Users>
        <User admin="True">
            <Name>Tim</Name>
            <location type="work">Office</location>
        </User>
        <User>
            <Name>Susan</Name>
            <location type="leasure">Garden</location>
        </User>
    </Users>


The description of the User does not change but now there is a new class
`Users` defining a sequence of users:

    @description
    class User:
        Name: str = ""
        location: str = ""

    @description
    class Users:
        users: list[User] = field(default_factory=list)
    
        @property
        def User(self):
            user = User()
            self.users.append(user)
            return user

    >>> users = Users()
    >>> users.load(root)
    >>> users
    Users(users=[User(Name='Tim', location='Office', attrib={'admin': 'True'}), User(Name='Susan', location='Garden', attrib={})], attrib={})
    
    
Because multiple `User`s must get stored in the `Users`-class, every
time when `User` is accessed as an attribute of `Users`, a new `User`
instance must get returned. This is the reason why the attribute `User`
is implemented as a property.  To keep a reference to the new `User`
instance, the instance is added to an internal `users`-list. This
`users`-list can have any name as long as it does not match a node-name.

Because the decorator `@description` converts a class into a dataclass,
mutable class attributes like lists or dicts must be declared as field
(imported from dataclasses) with a default_factory.

Iterating over all users can be done by iterating over all items of
`Users.users`:

    >>> for user in users.users:
    >>>     print(user)
    
    User(Name='Tim', location='Office', attrib={'admin': 'True'})
    User(Name='Susan', location='Garden', attrib={})
    

However it may feel more pythonic to iterate over the `users` instead of
`users.users`. This can be archieved by the help of the mixin class
`ListItemIteratorMixin`:

    @description
    class Users(ListItemIteratorMixin):
        list_items: list[User] = field(default_factory=list)
    
        @property
        def User(self):
            user = User()
            self.list_items.append(user)
            return user


Here `Users` inherit from `ListItemIteratorMixin` and the attribute
`users` changed to `list_items`. Now `Users` is an iterable:

    >>> for user in users:
    >>>     print(user)
    
    User(Name='Tim', location='Office', attrib={'admin': 'True'})
    User(Name='Susan', location='Garden', attrib={})


Handling mutable attributes
---------------------------

Let's take to following xml-structure describing users for a department:

    <department>
        <name>Research</name>
        <Users>
            <User admin="True">
                <Name>Tim</Name>
                <location type="work">Office</location>
            </User>
            <User>
                <Name>Susan</Name>
                <location type="leasure">Garden</location>
            </User>
        </Users>
    </department>


The `department`-node has two attributes: `name` which is of type str
and `Users` which is a sequence holding `User`-nodes. So `Users` is a
mutable for which a default-factory is needed:

    @description
    class Department:
        name: str = ""
        Users: Users = field(default_factory=Users)

    >>> department = Department()
    >>> department.load(root)
    >>> for user in department.Users:
    >>>     print(user)
    User(Name='Tim', location='Office', attrib={'admin': 'True'})
    User(Name='Susan', location='Garden', attrib={})
    
    
Again, the attribute `Users` is in uppercase, because it must match the
node-name. And because it is a mutable class-attribute of a dataclass,
it must be defined as a field with a default-factory.


Handling repetitions
--------------------

There is a subtle difference between sequences and repetitons. The
example with sequences works, because the `User` attribute represents a
node with subnodes. But if an attribute is a leaf-node, the value is
stored in the node directly, because a leaf node is inherited from type
string. Let's have an example:

    <collection>
        <name>Tim</name>
        <position>cook</position>
        <name>Susan</name>
        <position>chief</position>
    </collection>


    @description
    class Collection:
        name: str = ""
        position: str = ""
    
    >>> collection = Collection()
    >>> collection.load(root)
    >>> collection
    Collection(name='Susan', position='chief', attrib={})


Here the values of the attributes are overwritten one after the other
and just the last node-content will get stored (susan/chief). Also note
that the describing class of the root-node must not match the node-name.
So here the root-node `collection` is described by the `Collection`
class, but instead of `Collection` it could also be any name.
(That is, because .load() is called on the root-node which is already
instanciated.)

To store repetitions the leaf-names must be represented by propterties
storing the values in separate lists. So the properties must provide
getters and setters:

    @description
    class Collection:
        names: list = field(default_factory=list)
        positions: list = field(default_factory=list)
    
        # use property as decorator with a setter:
        @property
        def name(self):
            return ""
    
        @name.setter
        def name(self, value):
            self.names.append(value)
    
        # use property as a function with getter and setter as arguments:
        position = property(
            lambda self: "",
            lambda self, value: self.positions.append(value)
        ) 

    >>> collection = Collection()
    >>> collection.load(root)
    >>> collection
    Collection(names=['Tim', 'Susan'], positions=['cook', 'chief'], attrib={})


The attributes `name` and `position` are now implemented as properties
returning the default value (an empty string) and adding the value to an
internal list. This is also an example where it can be more convenient
to use property as a function, because it takes less code and fewer
lines. Now all attributes are stored – changing the xml to: 

    <collection type="kitchen">
        <name>Tim</name>
        <position location="Cologne">cook</position>
        <name>Susan</name>
        <position location="Berlin">chief</position>
    </collection>
    
    
Running the same code as before will result in     

    >>> collection = Collection()
    >>> collection.load(root)
    >>> collection
    Collection(names=['Tim', 'Susan'], positions=['cook', 'chief'], attrib={'type': 'kitchen'})


To iterate over the items, assuming that `name` and `position` are in
synchron order, just add an according method or property to the
Collection class:

    @description
    class Collection:
        names: list = field(default_factory=list)
        positions: list = field(default_factory=list)
        ...
        @property
        def entries(self):
            return zip(self.names, self.positions)


Now it is possible to iterate over the entries:

    >>> collection = Collection()
    >>> collection.load(root)
    >>> for name, position in collection.entries:
    >>>     print(f"Name: {name}, Position: {position}, {position.attrib}")
    
    Name: Tim, Position: cook, {'location': 'Cologne'}
    Name: Susan, Position: chief, {'location': 'Berlin'}


The additional methods and properties in a class decorated with
`@description` can have any names as long as they do not match an
xml-node name.
"""

from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from dataclasses import field
from fritzconnection.core.utils import localname


class _UnknownNode:
    """
    Marker class for unknown node names.
    Used internally.
    """


class Leaf(str):
    """
    String type with an additional attribute `attrib` for storing
    node-attributes.
    """
    __slots__ = ("attrib",)


def nodeloader(cls):
    """
    Class decorator to make a class a node-loader with an additional
    instance-attribute `attrib`. The decorator is designed to add the
    attribute to the set of instance attributes of a dataclass (what
    may not work by inheritance).
    """

    def load(self, root: ET.Element):
        self.attrib = root.attrib
        for node in root:
            node_name = localname(node)
            attr = getattr(self, node_name, _UnknownNode)
            if attr is _UnknownNode:
                # print(f"Unknown node: {node_name}")  # TODO: log on debug-level
                continue
            if hasattr(attr, "load") and callable(attr.load):
                attr.load(node)
            else:
                # node is a Leaf: -> str with attrib-attribute
                value = node.text
                if isinstance(value, str):  # should always be True
                    value = value.strip()
                leaf = Leaf(value)
                leaf.attrib = node.attrib
                setattr(self, node_name, leaf)
               
    # for a dataclass the annotation for an instance attribute
    # must be added explicitly:
    cls.attrib = field(default_factory=dict)
    cls.__annotations__["attrib"] = dict
    cls.load = load
    return cls


def description(cls):
    """
    Class decorator combining nodeloader and dataclass,
    if a dataclass is also a nodeloader (which are most classes).
    (enhances readability by avoiding stacked decorators.)
    """
    nodeloader(cls)
    dataclass(cls)
    return cls


class ListItemIteratorMixin:
    """
    Provides an __iter__ method for classes with a list_items attribute
    of type list, so that the instances are iterables with regard to the
    list_item list.
    """    
    def __iter__(self):
        return iter(self.list_items)

    def __len__(self) -> int:
        return len(self.list_items)


class DeviceDescriptionMixin:

    @property
    def devices(self) -> dict[str, Device]:
        return self.device.devices

    @property
    def spec_version(self) -> str:
        return str(self.specVersion)

    @property
    def services(self) -> dict[str, Service]:
        services = {}
        for device in self.devices.values():
            for service in device.serviceList:
                services[service.short_service_id] = service
        return services


@description
class BoxInfo:
    Name: str = ""
    HW: str = ""
    Version: str = ""
    Revision: str = ""
    Serial: str = ""
    OEM: str = ""
    Lang: str = ""
    Annex: str = ""
    Country: str = ""
    flags: list = field(default_factory=list)
    UpdateConfig: str = ""

    @property
    def Flag(self):
        return ""

    @Flag.setter
    def Flag(self, value):
        self.flags.append(value)

    @property
    def ident(self):
        return "-".join((self.HW, self.Version, self.Revision))

    @property
    def version(self):
        try:
            major, minor, patch = self.Version.split(".")
        except ValueError:
            version = ""
        else:
            version = f"{minor}.{patch}".lstrip("0")
        return version


@description
class IconList(ListItemIteratorMixin):
    list_items: list[Icon] = field(default_factory=list)

    @property
    def icon(self):
        icon = Icon()
        self.list_items.append(icon)
        return icon


@description
class Icon:
    mimetype: str = ""
    width: str = ""
    height: str = ""
    depth: str = ""
    url: str = ""


@description
class ServiceList(ListItemIteratorMixin):
    list_items: list[Service] = field(default_factory=list)

    @property
    def service(self):
        service = Service()
        self.list_items.append(service)
        return service


@description
class Service:
    serviceType: str = ""
    serviceId: str = ""
    controlURL: str = ""
    eventSubURL: str = ""
    SCPDURL: str = ""
    scpd: SCPD|None = None
    _actions: dict = field(default_factory=dict)
    _state_variables: dict = field(default_factory=dict)

    @property
    def short_service_id(self):
        return self.serviceId.split(":")[-1]

    @property
    def actions(self) -> dict:
        """
        Mapping of all actions provided by the service
        """
        if not self._actions:
            for action in self.scpd.actionList:
                self._actions[action.name] = action
        return self._actions

    @property
    def state_variables(self) -> dict:
        """
        Mapping of all state_variables for the action-arguments
        """
        if not self._state_variables:
            for state_variable in self.scpd.serviceStateTable:
                self._state_variables[state_variable.name] = state_variable
        return self._state_variables

    def get_max_argument_name_len(self) -> int:
        """
        Returns the length of the longest agrument-name from all actions.
        """
        return max(a.get_max_argument_name_len() for a in self.actions.values())


@description
class SpecVersion:
    major: str = ""
    minor: str = ""

    def __str__(self):
        return f"{self.major}.{self.minor}"


@description
class SystemVersion:
    HW: str = ""
    Major: str = ""
    Minor: str = ""
    Patch: str = ""
    Buildnumber: str = ""
    Display: str = ""

    def __str__(self) -> str:
        try:
            patch = f"{int(self.Patch):0>2d}"
        except ValueError:
            patch = self.Patch
        version = f"{self.Minor}.{patch}"
        if len(version) == 1:
            # just the dot
            version = ""
        return version

    @property
    def ident(self):
        return "-".join((self.HW, self.Display, self.Buildnumber))


@description
class DeviceList(ListItemIteratorMixin):
    list_items: list[Device] = field(default_factory=list)

    @property
    def device(self):
        device = Device()
        self.list_items.append(device)
        return device


@description
class Device:
    deviceType: str = ""
    friendlyName: str = ""
    manufacturer: str = ""
    manufacturerURL: str = ""
    modelDescription: str = ""
    modelName: str = ""
    modelNumber: str = ""
    modelURL: str = ""
    serialNumber: str = ""
    UPC: str = ""
    UDN: str = ""
    originUDN: str = ""
    presentationURL: str = ""
    iconList: IconList = field(default_factory=IconList)
    serviceList: ServiceList = field(default_factory=ServiceList)
    deviceList: DeviceList = field(default_factory=DeviceList)

    @property
    def short_device_type(self):
        try:
            result = self.deviceType.split(":")[-2]
        except IndexError:
            # unexpected deviceType format, return the original value
            result = self.deviceType
        return result

    @property
    def devices(self) -> dict[str, Device]:
        """
        Returns a mapping of devices: this device and all nested devices.
        """
        devices = {}
        devices[self.short_device_type] = self
        for device in self.deviceList:
            devices.update(device.devices)
        return devices

    def __str__(self):
        return f"{self.friendlyName}, {self.deviceType}"


@description
class ArgumentList(ListItemIteratorMixin):
    list_items: list[Argument] = field(default_factory=list)

    @property
    def argument(self):
        argument = Argument()
        self.list_items.append(argument)
        return argument


@description
class Argument:
    name: str = ""
    direction: str = ""
    relatedStateVariable: str = ""

    def get_report(self, indent=0, argument_textlen=0) -> str:
        """
        Returns a line describing the argument with name and direction.
        """
        if not argument_textlen:
            argument_textlen = len(self.name) + 1
        prefix = " " * indent
        # direction is in|out
        arrow = "-->  in" if len(self.direction) == 2 else "<-- out"
        return f"{prefix}{self.name:<{argument_textlen}}{arrow}"


@description
class ActionList(ListItemIteratorMixin):
    list_items: list[Action] = field(default_factory=list)

    @property
    def action(self):
        action = Action()
        self.list_items.append(action)
        return action


@description
class Action:
    name: str = ""
    argumentList: ArgumentList = field(default_factory=ArgumentList)
    _arguments: dict = field(default_factory=dict)

    @property
    def arguments(self) -> dict:
        if not self._arguments:
            for argument in self.argumentList:
                self._arguments[argument.name] = argument
        return self._arguments

    def get_max_argument_name_len(self) -> int:
        try:
            return len(max(self.arguments.keys(), key=lambda x: len(x)))
        except ValueError:
            return 0

    def get_report(
        self,
        indentation=0,
        argument_indentation=0,
        argument_textlen=0,
        report_arguments=False
    ) -> str:
        """
        Returns a multiline-string with the name of the action and a
        list of all arguments, line by line.
        """
        if not argument_indentation:
            argument_indentation = indentation + 2
        indentation = " " * indentation
        lines = [f"{indentation}{self.name}{':' if report_arguments else ''}"]
        if report_arguments:
            for argument in self.arguments.values():
                lines.append(
                    argument.get_report(argument_indentation, argument_textlen)
                )
        return "\n".join(lines)


@description
class ServiceStateTable(ListItemIteratorMixin):
    list_items: list[Action] = field(default_factory=list)

    @property
    def stateVariable(self):
        state_variable = StateVariable()
        self.list_items.append(state_variable)
        return state_variable


@description
class AllowedValueList(ListItemIteratorMixin):
    list_items: list[str] = field(default_factory=list)

    @property
    def allowedValue(self):
        return ""

    @allowedValue.setter
    def allowedValue(self, value):
        self.list_items.append(value)


@description
class StateVariable:
    name: str = ""
    dataType: str = ""
    defaultValue: str = ""
    allowedValueList: AllowedValueList = field(default_factory=AllowedValueList)


@description
class SCPD:
    specVersion: SpecVersion = field(default_factory=SpecVersion)
    actionList: ActionList = field(default_factory=ActionList)
    serviceStateTable: ServiceStateTable = field(default_factory=ServiceStateTable)


@description
class UPnPInternetGatewayDescription(DeviceDescriptionMixin):
    specVersion: SpecVersion = field(default_factory=SpecVersion)
    device: Device = field(default_factory=Device)


@description
class TR64Description(DeviceDescriptionMixin):
    specVersion: SpecVersion = field(default_factory=SpecVersion)
    systemVersion: SystemVersion = field(default_factory=SystemVersion)
    device: Device = field(default_factory=Device)

    @property
    def device_name(self):
        return self.device.modelName

    @property
    def system_version(self) -> str:
        return str(self.systemVersion)

    @property
    def ident(self):
        return self.systemVersion.ident


# --------------------------------------------------------
# helper classes for xml-content returned from lua-scripts

class AttributeCollectorMixin:
    """
    Class that creates new attributes on attribute-access instead of
    raising a KeyError.
    """
    def __getattr__(self, name):
        setattr(self, name, None)
        return getattr(self, name)


@nodeloader
class HostItem(AttributeCollectorMixin):
    pass


@description
class HostItems(ListItemIteratorMixin):
    list_items: list[HostItem] = field(default_factory=list)

    @property
    def Item(self):
        item = HostItem()
        self.list_items.append(item)
        return item


# --------------------------------------------------------
# helper classes for xml-content describing the device-log

@description
class Event:
    id: str = ""
    group: str = ""
    date: str = ""
    time: str = ""
    msg: str = ""

    @property
    def datetime(self) -> datetime.datetime:
        return datetime.datetime.strptime(f"{self.date}{self.time}", "%d.%m.%y%H:%M:%S")

@description
class DeviceLog(ListItemIteratorMixin):
    list_items: list[Event] = field(default_factory=list)
    
    @property
    def Event(self) -> Event:
        event = Event()
        self.list_items.append(event)
        return event


# --------------------------------------------------------
# helper classes for SessionInfo extracting
# (for session-ids)

@description
class Rights:
    names: list = field(default_factory=list)
    accesses: list = field(default_factory=list)

    Name = property(lambda self: "", lambda self, value: self.names.append(value))
    Access = property(lambda self: "", lambda self, value: self.accesses.append(value))

    def get(self):
        return {k: v for k, v in zip(self.names, self.accesses)}


@description
class Users(ListItemIteratorMixin):
    list_items: list = field(default_factory=list)
    User = property(lambda self: "", lambda self, value: self.list_items.append(value))
    

@description
class SessionInfo:
    SID: str = ""
    Challenge: str = ""
    BlockTime: str = ""
    users: Users | None = None
    _rights: Rights | None = None

    @property
    def rights(self):
        return self._rights.get()

    @property
    def last_user(self):
        for user in self.users:
            if user.attrib.get("last") == "1":
                return user
        return None
    
    @property
    def Rights(self):
        self._rights = Rights()
        return self._rights

    @property
    def Users(self):
        self.users = Users()
        return self.users
    

