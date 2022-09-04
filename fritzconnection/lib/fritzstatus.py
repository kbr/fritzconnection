"""
Module to read status-information from an AVM FritzBox.
"""

from collections import namedtuple
from warnings import warn

from .fritzbase import AbstractLibraryBase
from .fritztools import (
    ArgumentNamespace,
    format_dB,
    format_num,
    format_rate,
)

DefaultConnectionService = namedtuple(
    "DefaultConnectionService",
    "prefix connection_service postfix"
)

def _integer_or_original(value):
    """
    Tries to convert value to an integer. Returns this integer on
    success, otherwise returns the original value.
    """
    try:
        return int(value)
    except ValueError:
        return value


class FritzStatus(AbstractLibraryBase):
    """
    Class for requesting status-information: up, down, ip, activity
    (bytes per second send/received). All parameters are optional. If
    given, they have the following meaning: `fc` is an instance of
    FritzConnection, `address` the ip of the Fritz!Box, `port` the port
    to connect to, `user` the username, `password` the password,
    `timeout` a timeout as floating point number in seconds, `use_tls` a
    boolean indicating to use TLS (default False).
    """

    @property
    def is_linked(self):
        """
        A boolean whether the FritzBox is physically linked to
        the provider.
        """
        status = self.fc.call_action("WANCommonIFC", "GetCommonLinkProperties")
        return status["NewPhysicalLinkStatus"] == "Up"

    @property
    def is_connected(self):
        """
        A boolean whether the FritzBox has established an
        internet-connection.
        """
        status = self.fc.call_action("WANIPConn", "GetStatusInfo")
        return status["NewConnectionStatus"] == "Connected"

    @property
    def external_ip(self):
        """The external v4 ip-address."""
        return self.fc.call_action("WANIPConn", "GetExternalIPAddress")[
            "NewExternalIPAddress"
        ]

    @property
    def external_ipv6(self):
        """The external v6 ip-address."""
        return self.external_ipv6_info["NewExternalIPv6Address"]

    @property
    def external_ipv6_info(self):
        """
        Returns the ipv6 external address information as a dictionary with the keys:
        NewExternalIPv6Address                   out ->     string
        NewPrefixLength                          out ->     ui1
        NewValidLifetime                         out ->     ui4
        NewPreferedLifetime                      out ->     ui4
        """
        return self.fc.call_action("WANIPConn", "X_AVM_DE_GetExternalIPv6Address")

    @property
    def ipv6_prefix(self):
        """The internal v6 prefix."""
        return self.ipv6_prefix_info["NewIPv6Prefix"]

    @property
    def ipv6_prefix_info(self):
        """
        Returns the ipv6 prefix information as a dictionary with the keys:
        NewIPv6Prefix                            out ->     string
        NewPrefixLength                          out ->     ui1
        NewValidLifetime                         out ->     ui4
        NewPreferedLifetime                      out ->     ui4
        """
        return self.fc.call_action("WANIPConn", "X_AVM_DE_GetIPv6Prefix")

    @property
    def connection_uptime(self):
        """Connection uptime in seconds."""
        status = self.fc.call_action("WANIPConn", "GetStatusInfo")
        return status["NewUptime"]

    @property
    def uptime(self):
        """
        .. deprecated:: 1.9.0
           Use :func:`connection_uptime` instead.
        """
        warn('This method is deprecated. Use "connection_uptime" instead.', DeprecationWarning)
        return self.connection_uptime

    @property
    def device_uptime(self):
        """Device uptime in seconds."""
        status = self.fc.call_action("DeviceInfo1", "GetInfo")
        return status["NewUpTime"]

    @property
    def str_uptime(self):
        """Connection uptime in human-readable format."""
        mins, secs = divmod(self.uptime, 60)
        hours, mins = divmod(mins, 60)
        return "%02d:%02d:%02d" % (hours, mins, secs)

    @property
    def bytes_sent(self):
        """Total number of sent bytes."""
        try:
            status = self.fc.call_action("WANCommonIFC1", "GetAddonInfos")
            value = status["NewX_AVM_DE_TotalBytesSent64"]
        except KeyError:
            # fallback for older FritzOS Versions not providing a 64 bit value:
            status = self.fc.call_action(
                "WANCommonIFC1", "GetTotalBytesSent"
            )
            value = status["NewTotalBytesSent"]
        return _integer_or_original(value)

    @property
    def bytes_received(self):
        """Total number of received bytes."""
        try:
            status = self.fc.call_action("WANCommonIFC1", "GetAddonInfos")
            value = status["NewX_AVM_DE_TotalBytesReceived64"]
        except KeyError:
            # fallback for older FritzOS Versions not providing a 64 bit value:
            status = self.fc.call_action(
                "WANCommonIFC1", "GetTotalBytesReceived"
            )
            value = status["NewTotalBytesReceived"]
        return _integer_or_original(value)

    @property
    def transmission_rate(self):
        """
        The upstream and downstream values as a tuple in bytes per
        second. Use this for periodical calling.
        """
        status = self.fc.call_action("WANCommonIFC1", "GetAddonInfos")
        upstream = status["NewByteSendRate"]
        downstream = status["NewByteReceiveRate"]
        return upstream, downstream

    @property
    def str_transmission_rate(self):
        """
        Tuple of human-readable transmission rate in bytes. First item
        is upstream, second item downstream.
        """
        upstream, downstream = self.transmission_rate
        return (format_num(upstream), format_num(downstream))

    @property
    def max_linked_bit_rate(self):
        """
        Tuple with the maximum upstream- and downstream-rate
        of the physical link. The rate is given in bits/sec.
        """
        return self._get_max_bit_rate("WANCommonInterfaceConfig")

    @property
    def max_bit_rate(self):
        """
        Tuple with the maximum upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        return self._get_max_bit_rate("WANCommonIFC")

    def _get_max_bit_rate(self, servicename):
        """
        internal method to get the upstream and downstream-rates for
        different services of the WANCommonInterfaceConfig1 ServiceType.
        """
        status = self.fc.call_action(servicename, "GetCommonLinkProperties")
        downstream = status["NewLayer1DownstreamMaxBitRate"]
        upstream = status["NewLayer1UpstreamMaxBitRate"]
        return upstream, downstream

    @property
    def max_byte_rate(self):
        """
        Same as max_bit_rate but rate is given in bytes/sec.
        """
        upstream, downstream = self.max_bit_rate
        return upstream / 8.0, downstream / 8.0

    @property
    def str_max_linked_bit_rate(self):
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
    def str_max_bit_rate(self):
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

    def get_monitor_data(self, sync_group_index=0):
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
                    monitor_data[key] = items
        return monitor_data

    def reconnect(self):
        """Makes a reconnection with a new external ip."""
        self.fc.reconnect()

    @property
    def noise_margin(self):
        """
        Tuple of noise margin. First item
        is upstream, second item downstream.
        """
        status = self.fc.call_action("WANDSLInterfaceConfig1", "GetInfo")
        upstream = status["NewUpstreamNoiseMargin"]
        downstream = status["NewDownstreamNoiseMargin"]
        return upstream, downstream

    @property
    def str_noise_margin(self):
        """
        Human-readable noise margin in dB. Value is a tuple, first item
        is upstream, second item downstream.
        """
        upstream, downstream = self.noise_margin
        return (format_dB(upstream), format_dB(downstream))

    @property
    def attenuation(self):
        """
        Tuple of attenuation. First item
        is upstream, second item downstream.
        """
        status = self.fc.call_action("WANDSLInterfaceConfig1", "GetInfo")
        upstream = status["NewUpstreamAttenuation"]
        downstream = status["NewDownstreamAttenuation"]
        return upstream, downstream

    @property
    def str_attenuation(self):
        """
        Human-readable attenuation in dB. Value is a tuple, first item
        is upstream, second item downstream.
        """
        upstream, downstream = self.attenuation
        return (format_dB(upstream), format_dB(downstream))

    @property
    def upnp_enabled(self):
        """
        Returns a boolean whether upnp is enabled or raises a
        FritzServiceError in case the service is not available.
        """
        status = self.fc.call_action("X_AVM-DE_UPnP1", "GetInfo")
        return status["NewEnable"]

    @property
    def device_has_mesh_support(self):
        """
        True if the device supports mesh, otherwise False.
        """
        # check for the corresponding action
        # whether mesh is supported
        try:
            return (
                "X_AVM-DE_GetMeshListPath"
                in self.fc.services["Hosts1"].actions
            )
        except KeyError:
            # can happen if "Hosts1" is not known
            return False

    def get_device_info(self):
        """
        Returns an ArgumentNamespace with the attributes:

        manufacturer_name, manufacturer_oui, model_name, description,
        product_class, serial_number, software_version, hardware_version,
        spec_version, provisioning_code, up_time, device_log

        .. versionadded:: 1.10

        """
        return ArgumentNamespace(self.fc.call_action("DeviceInfo1", "GetInfo"))

    def get_default_connection_service(self):
        """
        Returns a namedtuple of type DefaultConnectionService:
        `prefix` -> str
        `device_connection` -> str (like "WANPPPConnection")
        `postfix` -> str
        """
        result = self.fc.call_action(
                "Layer3Forwarding1", "GetDefaultConnectionService"
        )
        prefix, connection_service, postfix = \
            result["NewDefaultConnectionService"].split('.', 2)
        return DefaultConnectionService(
            prefix, connection_service, postfix
        )

    @property
    def connection_service(self):
        """
        The extracted connection_service from
        get_default_connection_service().
        """
        result = self.get_default_connection_service()
        return result.connection_service

    @property
    def update_available(self):
        """
        The new version number (as a string) if an update is available or an
        empty string if no update is avilable.
        """
        return self.fc.call_action("UserInterface1", "GetInfo")["NewX_AVM-DE_Version"]

    @property
    def has_wan_enabled(self):
        """
        True if wan is enabled otherwise False.
        """
        return self.fc.call_action(self.connection_service, "GetInfo")["NewEnable"]

    @property
    def has_wan_support(self):
        """
        True is the device supports a WAN interface.
        False otherwise.
        """
        return "Layer3Forwarding1" in self.fc.services
