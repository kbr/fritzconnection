"""
Loads the description files from the device describing the API. A device
can be a router or a repeater.
"""
from __future__ import annotations

import xml.etree.ElementTree as ET

from dataclasses import dataclass
from dataclasses import field

#from fritzconnection.core.utils import get_xml_root
from fritzconnection.core.utils import localname


def list_items_iterable(cls):
    """
    Class decorator to make a List-class with an iterable `list_items`
    attribut an iterable iterating over the `list_items` attribute.
    """
    def __iter__(self):
        return iter(self.list_items)

    cls.__iter__ = __iter__
    return cls


class UnknownNode:
    """
    Marker class for unknown node names.
    """


class Loader:
    """
    Class for recursive node-loading.
    """
    attrib: dict|None = None

    def load(self, root: ET.Element):
        self.attrib = root.attrib
        for node in root:
            node_name = localname(node)
            attr = getattr(self, node_name, UnknownNode)
            if attr is UnknownNode:
                # print(f"Unknown node: {node_name}")
                continue
            if isinstance(attr, Loader):
                attr.load(node)
            else:
                value = node.text
                if isinstance(value, str):
                    # should always be True:
                    value = value.strip()
                setattr(self, node_name, value)


@dataclass
@list_items_iterable
class IconList(Loader):
    list_items: list[Icon] = field(default_factory=list)

    @property
    def icon(self):
        icon = Icon()
        self.list_items.append(icon)
        return icon


@dataclass
class Icon(Loader):
    mimetype: str = ""
    width: str = ""
    height: str = ""
    depth: str = ""
    url: str = ""


@dataclass
@list_items_iterable
class ServiceList(Loader):
    list_items: list[Service] = field(default_factory=list)

    @property
    def service(self):
        service = Service()
        self.list_items.append(service)
        return service


@dataclass
class Service(Loader):
    serviceType: str = ""
    serviceId: str = ""
    controlURL: str = ""
    eventSubURL: str = ""
    SCPDURL: str = ""

    @property
    def short_id(self):
        return self.serviceId.split(":")[-1]


@dataclass
class SpecVersion(Loader):
    major: str = ""
    minor: str = ""

    def __str__(self):
        return f"{self.major}.{self.minor}"


@dataclass
class SystemVersion(Loader):
    HW: str = ""
    Major: str = ""
    Minor: str = ""
    Patch: str = ""
    Buildnumber: str = ""
    Display: str = ""


@dataclass
@list_items_iterable
class DeviceList(Loader):
    list_items: list[Device] = field(default_factory=list)

    @property
    def device(self):
        device = Device()
        self.list_items.append(device)
        return device


@dataclass
class Device(Loader):
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

    def get_devices(self):
        devices = [self]
        for device in self.deviceList:
            devices.extend(device.get_devices())
        return devices

    def __str__(self):
        return f"{self.friendlyName}, {self.deviceType}"


@dataclass
@list_items_iterable
class ArgumentList(Loader):
    list_items: list[Argument] = field(default_factory=list)

    @property
    def argument(self):
        argument = Argument()
        self.list_items.append(argument)
        return argument


@dataclass
class Argument(Loader):
    name: str = ""
    direction: str = ""
    relatedStateVariable: str = ""


@dataclass
@list_items_iterable
class ActionList(Loader):
    list_items: list[Action] = field(default_factory=list)

    @property
    def action(self):
        action = Action()
        self.list_items.append(action)
        return action


@dataclass
class Action(Loader):
    name: str = ""
    argumentList: list[Argument] = field(default_factory=list)


@dataclass
@list_items_iterable
class ServiceStateTable(Loader):
    list_items: list[Action] = field(default_factory=list)

    @property
    def stateVariable(self):
        state_variable = StateVariable()
        self.list_items.append(state_variable)
        return state_variable


@dataclass
@list_items_iterable
class AllowedValueList(Loader):
    list_items: list[str] = field(default_factory=list)

    @property
    def allowedValue(self):
        return ""

    @allowedValue.setter
    def allowedValue(self, value):
        self.list_items.append(value)


@dataclass
class StateVariable(Loader):
    name: str = ""
    dataType: str = ""
    defaultValue: str = ""
    allowedValueList: AllowedValueList = field(default_factory=AllowedValueList)


@dataclass
class SCPD(Loader):
    specVersion: SpecVersion = field(default_factory=SpecVersion)
    actionList: ActionList = field(default_factory=ActionList)
    serviceStateTable: ServiceStateTable = field(default_factory=ServiceStateTable)


# class DeviceDescriptionMixin:
#
#     @property
#     def devices(self):
#         return self.device.get_devices()


@dataclass
class UpnPInternetGatewayDescription(Loader):
    specVersion: SpecVersion = field(default_factory=SpecVersion)
    device: Device = field(default_factory=Device)

    @property
    def devices(self):
        return self.device.get_devices()

    @property
    def spec_version(self):
        return str(self.specVersion)


@dataclass
class TR64Description(Loader):
    specVersion: SpecVersion = field(default_factory=SpecVersion)
    systemVersion: SystemVersion = field(default_factory=SystemVersion)
    device: Device = field(default_factory=Device)

    @property
    def devices(self):
        return self.device.get_devices()
