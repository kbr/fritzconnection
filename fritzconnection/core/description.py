"""
Definition of all description nodes as dataclasses with methods for parsing.
"""

from __future__ import annotations

import xml.etree.ElementTree as ET

from dataclasses import dataclass
from dataclasses import field
from fritzconnection.core.utils import localname


FRITZ_IGD_DESC_FILE = "igddesc.xml"
FRITZ_TR64_DESC_FILE = "tr64desc.xml"


class _UnknownNode:
    """
    Marker class for unknown node names.
    Used internally.
    """

class ListItemIteratorMixin:
    """
    Provides an __iter__ method for classes with a list_items attribute
    of type list, so that the instances are iterables with regard to the
    list_item list.
    """
    def __iter__(self):
        return iter(self.list_items)

    def __len__(self):
        return len(self.list_items)


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
                value = node.text
                if isinstance(value, str):  # should always be True
                    value = value.strip()
                setattr(self, node_name, value)

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


# ------------------------------------------------------------------------
# classes for igd- and tr64-description parsing. The classes may
# have attributes violation pep 8 but representing the original node-names
# of the xml-sources.


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
    def actions(self):
        """
        Mapping of all actions provided by the service
        """
        if not self._actions:
            for action in self.scpd.actionList:
                self._actions[action.name] = action
        return self._actions

    @property
    def state_variables(self):
        """
        Mapping of all state_variables for the action-arguments
        """
        if not self._state_variables:
            for state_variable in self.scpd.serviceStateTable:
                self._state_variables[state_variable.name] = state_variable
        return self._state_variables


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

    def __str__(self):
        return f"{self.Minor}.{int(self.Patch):0>2d}"


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
        return self.deviceType.split(":")[-2]

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
    def arguments(self):
        if not self._arguments:
            for argument in self.argumentList:
                self._arguments[argument.name] = argument
        return self._arguments


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
