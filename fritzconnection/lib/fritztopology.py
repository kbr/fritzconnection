"""
Module to access to the Mesh Topology
See https://avm.de/service/schnittstellen/ "Mesh-Topologie"
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Authors: Klaus Bremer

# code partly to dynamic for a useful mypy run:
# mypy: disable-error-code="attr-defined"

from __future__ import annotations

from .fritzhosts import FritzHosts
from .fritzbase import AbstractLibraryBase


class Connection:
    """
    Represents a connection from one device to another device.
    This is basically a convenience wrapper for InterfaceLink
    exposing the devices and some instance attributes in a more
    comfortable way.

    self.source is the origin device
    self.target is the connected device
    self.type is the connection type (like "WLAN")
    self.state is the connection state (like "DISCONNECTED", "CONNECTED")

    self.max_rx, max_tx, cur_rx and cur_tx are the maximum and
    current throughput data rates in kbit/sec.

    tx is the upload-throughput from source to target, even if the
    source is represented by the interface-link node 2.
    """

    def __init__(self, source, target, interface_link):
        self.source = source
        self.target = target
        self.interface_link = interface_link

    @property
    def type(self) -> str | None:
        return self._get_interface_attribute("type")

    @property
    def state(self) -> str | None:
        return self._get_interface_attribute("state")

    @property
    def max_rx(self) -> int | None:
        return self._get_transfer_rate("max_data_rate_rx")

    @property
    def max_tx(self) -> int | None:
        return self._get_transfer_rate("max_data_rate_tx")

    @property
    def cur_rx(self) -> int | None:
        return self._get_transfer_rate("cur_data_rate_rx")

    @property
    def cur_tx(self) -> int | None:
        return self._get_transfer_rate("cur_data_rate_tx")

    def _get_transfer_rate(self, name):
        """
        Adapt the rate to the link direction: 'tx' is the transfer rate
        from node 1 to node 2 which is ok, if node 1 represents the
        'source' node. In case it is the other way around the commands
        'tx' and 'rx' must get exchanged.
        """
        if self.interface_link.source_index == 2:
            name, direction = name.rsplit("_", 1)
            direction = "rx" if direction == "tx" else "tx"
            name = f"{name}_{direction}"
        return self._get_interface_attribute(name)

    def _get_interface_attribute(self, name, default=None):
        return getattr(self.interface_link, name, default)


class InterfaceLink:
    """
    Represents a node-link from an Interface of a device
    to another Interface of another device.
    (These are the vertexes of the mesh.)

    Instance attributes are all elements described as "node_links.properties"
    in the AVM documentation and accessible by their names, i.e. like
    'self.last_connected' in case the UNIX timestamp is requested.
    """

    def __init__(self, data: dict, interface: Interface):
        self.__dict__.update(data)
        self.interface = interface
        # The starting point is assumed to be the device, which is
        # the owner of self.interface.
        if self.node_interface_1_uid == self.interface.uid:
            self.source_index = 1
            self.target_index = 2
        else:
            self.source_index = 2
            self.target_index = 1

    def __repr__(self) -> str:
        return f"InterfaceLink:  {self.uid:<8}target-interface:  {self.node_interface_2_uid}"

    def __str__(self) -> str:
        connection = Connection(self.source, self.target, self)
        if connection.cur_tx is not None:
            throughput = connection.cur_tx // 1000  # from kB/s to MB/s
        else:
            throughput = None  # not known
        return f"from {self.source.name} to {self.target.name} (-> {throughput} MBit/s)"

    @property
    def source(self) -> Device:
        return self._get_connected_device(target=False)

    @property
    def target(self) -> Device:
        return self._get_connected_device(target=True)

    def get_connection(self) -> Connection:
        """
        Returns a connection instance describing a connection
        from one device to another device.
        """
        return Connection(self.source, self.target, self)

    def _get_connected_device(self, target=True):
        """
        Returns the device connected by this link,
        either the target or source device.
        """
        index = self.target_index if target else self.source_index
        device_id = getattr(self, f"node_{index}_uid")
        return self.interface.device.mesh.get_device_by_id(device_id)


class Interface:
    """
    An interface represents a physical infrastructure of a device
    to connect with other devices.
    An interface is part of a device and able to connect to another
    interface of another device.
    A connection is represented by the InterfaceLink class.
    """

    def __init__(self, data: dict, device: Device):
        self.__dict__.update(data)
        self.interface_links = [
            InterfaceLink(link, self) for link in self.node_links
        ]
        self.device = device

    def __repr__(self) -> str:
        representation = (
            f"Interface:  mac={self.mac:<20}"
            f"uid={self.uid:<8}"
            f"type={self.type:<8}"
        )
        if self.name:
            representation = f"{representation}name={self.name}"
        return representation

    def __str__(self) -> str:
        interface = repr(self)
        if self.interface_links:
            space = " " * 8
            links = f"\n{space}".join(str(link) for link in self.interface_links)
            interface = f"{interface}\n{space}{links}"
        return interface

    @property
    def mac(self) -> str:
        """mac address of the interface"""
        return self.mac_address

    def get_connections(self):
        """
        Returns a list of Connection objects describing all devices
        connected by this interface.
        """
        return [link.get_connection() for link in self.interface_links]


class Device:
    """
    A Device represents a physical item in the mesh, like a router,
    repeater, a laptop, a cell phone and other devices.
    (This is a node of the mesh.)

    Instance attributes created dynamical according to the
    AVM mesh topology schema: https://avm.de/service/schnittstellen/

    For convenience there are some properties and methods to access
    the data in a more mnemonic way.
    """

    def __init__(self, data: dict, mesh: FritzMeshTopology):
        self.__dict__.update(data)
        self.interfaces = [
            Interface(interface_data, self)
            for interface_data in self.node_interfaces
        ]
        self.mesh = mesh

    def __repr__(self) -> str:
        return f"Device:  mac={self.mac:<20}uid={self.uid:<8}{self.name}"

    def __str__(self) -> str:
        representation = repr(self)
        space = " "  * 4
        interfaces = f"\n{space}".join(str(interface) for interface in self.interfaces)
        return f"{representation}\n{space}{interfaces}"

    @property
    def name(self) -> str:
        return self.device_name

    @property
    def model(self) -> str:
        return self.device_model

    @property
    def vendor(self) -> str:
        return self.device_manufacturer

    @property
    def mac(self) -> str:
        return self.device_mac_address

    def get_connections(self):
        """
        Returns a list of Connection objects describing all
        devices connected to this device.
        """
        connections = []
        for interface in self.interfaces:
            connections.extend(interface.get_connections())
        return connections


class FritzMeshTopology(AbstractLibraryBase):
    """
    Represents the mesh topology with nodes representing the devices.

    """

    def __init__(self, fc=None, *args, **kwargs):
        super().__init__(fc, *args, **kwargs)
        self._fritzhosts = FritzHosts(self.fc)
        self.topology = {}
        self.nodes = {}

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}: "
            f"schema_version={self.schema_version}, "
            f"registered Devices: {self.number_of_devices}"
        )

    def __str__(self) -> str:
        nodes = "\n\n".join(str(device) for device in self.devices)
        return f"{repr(self)}\n{nodes}"

    @property
    def schema_version(self) -> str:
        return self.topology.get("schema_version", "unknown")

    @property
    def number_of_devices(self) -> int:
        return len(self.nodes)

    @property
    def devices(self) -> list[Device]:
        return list(self.nodes.values())

    def get_device_by_id(self, uid: str) -> Device:
        """
        Returns a device by id. The id is the node-uid like "n-1".
        The node-uids are fixed to devices after calling
        `load_topology()` but may change if `load_topology()` gets
        called again.
        """
        return self.nodes[uid]

    def load_topology(self):
        """
        Load the topology from the router.
        """
        self.topology = self._fritzhosts.get_mesh_topology(raw=False)
        self.nodes = {
            node["uid"]: Device(node, self)
            for node in self.topology.get("nodes", ())
        }
