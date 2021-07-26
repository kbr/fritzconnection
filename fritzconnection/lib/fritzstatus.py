"""
Modul to read status-informations from an AVM FritzBox.
"""

import time

from ..core.exceptions import FritzServiceError
from .fritzbase import AbstractLibraryBase
from .fritztools import format_num, format_rate, format_dB


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
    Class for requesting status-informations: up, down, ip, activity
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
        Returns the ipv6 external address informations as a dictionary with the keys:
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
        Returns the ipv6 prefix informations as a dictionary with the keys:
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
        Connection uptime in seconds.
        Alias for self.connection_uptime for backward compatibility.
        """
        return self.connection_uptime

    @property
    def device_uptime(self):
        """Device uptime in seconds."""
        status = self.fc.call_action("DeviceInfo1", "GetInfo")
        return status["NewUpTime"]

    @property
    def str_uptime(self):
        """Connection uptime in human readable format."""
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
        Tuple of human readable transmission rate in bytes. First item
        is upstream, second item downstream.
        """
        upstream, downstream = self.transmission_rate
        return (format_num(upstream), format_num(downstream))

    @property
    def max_linked_bit_rate(self):
        """
        Tuple with the maximun upstream- and downstream-rate
        of the physical link. The rate is given in bits/sec.
        """
        return self._get_max_bit_rate("WANCommonInterfaceConfig")

    @property
    def max_bit_rate(self):
        """
        Tuple with the maximun upstream- and downstream-rate
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
        Human readable maximum of the physical upstream- and
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
        Human readable maximum of the upstream- and downstream-rate in
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
        Human readable noise margin in dB. Value is a tuple, first item
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
        Human readable attenuation in dB. Value is a tuple, first item
        is upstream, second item downstream.
        """
        upstream, downstream = self.attenuation
        return (format_dB(upstream), format_dB(downstream))

