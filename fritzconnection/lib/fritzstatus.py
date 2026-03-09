"""
Module to read status-information from a FritzBox router.
Since v2.0 this module is mainly a glue-module for backward compatibility.
"""

import datetime
from dataclasses import field

from fritzconnection import FritzConnection
from fritzconnection.core.description import DeviceLog
from fritzconnection.core.exceptions import FritzConnectionException
from fritzconnection.core.exceptions import FritzServiceError
from fritzconnection.core.utils import get_xml_root
from fritzconnection.lib.fritztools import ArgumentNamespace
from fritzconnection.lib.fritztools import format_dB
from fritzconnection.lib.fritztools import format_num
from fritzconnection.lib.fritztools import format_rate
from fritzconnection.lib.fritzwan import FritzWAN


NO_WAN_DEVICE_ERROR_MESSAGE = "Device is not a WAN device."
NO_DSL_DEVICE_ERROR_MESSAGE = "Device is not a DSL device."


# DefaultConnectionService = namedtuple(
#     "DefaultConnectionService", "prefix connection_service postfix"
# )


class FritzStatus:
    """
    Class for providing status-information about the device and WAN connections
    """
    
    def __init__(self, fc=None, **kwargs):
        if fc is None:
            fc = FritzConnection(**kwargs)
        self.fc = fc
        try:
            self._fwan = FritzWAN(self.fc)
        except FritzServiceError:
            # will happen on non-WAN devices
            self._fwan = None
            
    @property
    def fwan(self):
        if not self._fwan:
            raise FritzConnectionException(NO_WAN_DEVICE_ERROR_MESSAGE)
        return self._fwan

    @property
    def wan_status_information(self) -> dict:
        """
        Provides a dict with the current WAN stus information. Raises a
        FritzConnectionException in case the device is not a WAN device.
        """
        return self.fwan.get_status_information()
            
    @property
    def has_wan_support(self) -> bool:
        """
        True if the device supports a WAN interface.
        False otherwise.
        """
        return self.fc.has_wan_support
        
    @property
    def is_linked(self) -> bool:
        """
        A boolean whether the FritzBox is physically linked to
        the provider.
        """
        return self.fwan.is_linked

    @property
    def is_connected(self) -> bool:
        """
        A boolean whether the FritzBox has established an
        internet-connection.
        """
        return self.fwan.is_connected
        
    @property
    def has_wan_enabled(self) -> bool:
        """
        True if wan is enabled otherwise False.
        This is a legathy alias to `is_connected`.
        """
        return self.is_connected

    @property
    def external_ip(self) -> str:
        """The external v4 ip-address."""
        return self.fwan.external_ip

    @property
    def external_ipv6(self) -> str:
        """The external v6 ip-address."""
        return self.fwan.external_ipv6
        
    @property
    def external_ipv6_info(self) -> dict:
        """
        Returns the ipv6 external address information as a dictionary with the keys:
        NewExternalIPv6Address                   out ->     string
        NewPrefixLength                          out ->     ui1
        NewValidLifetime                         out ->     ui4
        NewPreferedLifetime                      out ->     ui4
        """
        return self.fwan.external_ipv6_info

    @property
    def ipv6_prefix(self):
        """The internal v6 prefix."""
        return self.fwan.ipv6_prefix_info["NewIPv6Prefix"]

    @property
    def ipv6_prefix_info(self) -> dict:
        """
        Returns the ipv6 prefix information as a dictionary with the keys:
        NewIPv6Prefix                            out ->     string
        NewPrefixLength                          out ->     ui1
        NewValidLifetime                         out ->     ui4
        NewPreferedLifetime                      out ->     ui4
        """
        return self.fwan.ipv6_prefix_info
        
    @property
    def connection_uptime(self) -> int:
        """Connection uptime in seconds."""
        return  self.fwan.connection_uptime

    @property
    def str_uptime(self) -> str:
        """Connection uptime in human-readable format."""
        mins, secs = divmod(self.connection_uptime, 60)
        hours, mins = divmod(mins, 60)
        return "%02d:%02d:%02d" % (hours, mins, secs)

    @property
    def device_uptime(self) -> int:
        """Device uptime in seconds."""
        return self.fc.device_uptime

    @property
    def bytes_sent(self) -> int | str:
        """
        Total number of sent bytes.
        """
        addoninfo = self.fwan.get_addon_info()
        return addoninfo["NewTotalBytesSent"]

    @property
    def bytes_received(self) -> int:
        """
        Total number of received bytes.
        """
        addoninfo = self.fwan.get_addon_info()
        return addoninfo["NewTotalBytesReceived"]

    @property
    def transmission_rate(self) -> tuple[int, int]:
        """
        The upstream and downstream values as a tuple in bytes per
        second.
        """
        addoninfo = self.fwan.get_addon_info()
        upstream = addoninfo["NewByteSendRate"]
        downstream = addoninfo["NewByteReceiveRate"]
        return upstream, downstream

    @property
    def str_transmission_rate(self) -> tuple[str, str]:
        """
        Tuple of human-readable transmission rate in bytes. First item
        is upstream, second item downstream.
        """
        upstream, downstream = self.transmission_rate
        return format_num(upstream), format_num(downstream)

    @property
    def max_linked_bit_rate(self) -> tuple[int, int]:
        """
        Tuple with the maximum upstream- and downstream-rate
        of the physical link. The rate is given in bits/sec.
        """
        return self.fwan.max_linked_bit_rate

    @property
    def max_bit_rate(self) -> tuple[int, int]:
        """
        Tuple with the maximum upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        properties = self.fwan.get_common_link_properties()
        up = properties["NewLayer1UpstreamMaxBitRate"]
        down = properties["NewLayer1DownstreamMaxBitRate"]
        return up, down

    @property
    def max_byte_rate(self) -> tuple[float, float]:
        """
        Same as max_bit_rate but rate is given in bytes/sec.
        """
        upstream, downstream = self.max_bit_rate
        return upstream / 8.0, downstream / 8.0

    @property
    def str_max_linked_bit_rate(self) -> tuple[str, str]:
        """
        Human-readable maximum of the physical upstream- and
        downstream-rate in bits/sec. Value is a tuple, first item is
        upstream, second item is downstream.
        """
        upstream, downstream = self.max_linked_bit_rate
        return (
            format_rate(upstream, unit="bits"),
            format_rate(downstream, unit="bits"),
        )

    @property
    def str_max_bit_rate(self) -> tuple[str, str]:
        """
        Human-readable maximum of the upstream- and downstream-rate in
        bits/sec, as given by the provider. Value is a tuple, first item
        is upstream, second item is downstream.
        """
        upstream, downstream = self.max_bit_rate
        return (
            format_rate(upstream, unit="bits"),
            format_rate(downstream, unit="bits"),
        )

    def get_monitor_data(self, sync_group_index=0) -> dict:
        """
        Returns a dictionary with realtime data about the current up-
        and downstream rates.
        """
        monitor_data = self.fc.call_action(
            "WANCommonInterfaceConfig1",
            "X_AVM-DE_GetOnlineMonitor",
            NewSyncGroupIndex=sync_group_index,
        )
        for key, value in monitor_data.items():
            if isinstance(value, str) and "," in value:
                try:
                    items = [int(v) for v in value.split(",")]
                except (AttributeError, ValueError):
                    # ignore and keep value as is:
                    pass
                else:
                    monitor_data[key] = items  # type: ignore
        return monitor_data

    def reconnect(self) -> None:
        """Makes a reconnection with a new external ip."""
        self.fc.reconnect()

    @property
    def noise_margin(self) -> tuple[int, int]:
        """
        Tuple of noise margin. First item
        is upstream, second item downstream.
        """
        try:
            return self.fwan.noise_margin
        except AttributeError:
            raise FritzConnectionException(NO_DSL_DEVICE_ERROR_MESSAGE)

    @property
    def str_noise_margin(self) -> tuple[str, str]:
        """
        Human-readable noise margin in dB. Value is a tuple, first item
        is upstream, second item downstream.
        """
        upstream, downstream = self.noise_margin
        return format_dB(upstream), format_dB(downstream)

    @property
    def attenuation(self) -> tuple[int, int]:
        """
        Tuple of attenuation. First item
        is upstream, second item downstream.
        """
        try:
            return self.fwan.attenuation
        except AttributeError:
            raise FritzConnectionException(NO_DSL_DEVICE_ERROR_MESSAGE)

    @property
    def str_attenuation(self) -> tuple[str, str]:
        """
        Human-readable attenuation in dB. Value is a tuple, first item
        is upstream, second item downstream.
        """
        upstream, downstream = self.attenuation
        return format_dB(upstream), format_dB(downstream)

    @property
    def upnp_enabled(self) -> bool:
        """
        Returns a boolean whether upnp is enabled or raises a
        FritzServiceError in case the service is not available.
        """
        status = self.fc.call_action("X_AVM-DE_UPnP1", "GetInfo")
        return status["NewEnable"]

    @property
    def device_has_mesh_support(self) -> bool:
        """
        True if the device supports mesh, otherwise False.
        """
        return self.fc.has_mesh_support

    @property
    def connection_service(self) -> str:
        """
        The connection_service as string.
        """
        return self.fwan.service

    @property
    def update_available(self) -> str:
        """
        The new version number (as a string) if an update is available or an
        empty string if no update is avilable.
        """
        return self.fc.call_action("UserInterface1", "GetInfo")["NewX_AVM-DE_Version"]

    def get_device_info(self) -> ArgumentNamespace:
        """
        Returns an ArgumentNamespace with the attributes:

        manufacturer_name, manufacturer_oui, model_name, description,
        product_class, serial_number, software_version, hardware_version,
        spec_version, provisioning_code, up_time, device_log

        .. versionadded:: 1.10

        """
        return ArgumentNamespace(self.fc.call_action("DeviceInfo1", "GetInfo"))
        
    def get_device_log(self, filter: str | None = None) -> DeviceLog:
        """
        The device log is a list of events with the attributes `id`,
        `group`, `date`, `time` and `msg` holding information like "DSL
        synchronization starting (training)" and other system messages.
        The Method returns a DeviceLog instance holding a list of Event
        instances. The DeviceLog instance is an iterable and can be
        used on a FritzStatus instance like:

        >>> device_log = fritzstatus.get_avm_device_log()
        >>> for event in device_log:
        >>>     print(event.datetime, event.msg)

        The returned events can be filtered by groups like 'sys', 'net',
        'fon', 'wlan' or 'usb'. To filter by a group provide the
        group-name as filter-argument.
        """
        result = self.fc.call_action("DeviceInfo1", "X_AVM-DE_GetDeviceLogPath")
        path = result["NewDeviceLogPath"]
        if filter:
            path = f"{path}&filter={filter}"
        url = f"{self.fc.address}{path}"
        root_node = get_xml_root(url, session=self.fc.session)
        device_log = DeviceLog()
        device_log.load(root_node)
        return device_log

    def get_avm_device_log(self, filter: str | None = None) -> DeviceLog:
        """
        Alias for backward compatibility.
        
        .. version-deprecated:: 2.0
           Use :py:func:`get_device_log` instead.
        """
        return self.get_device_log(filter)
