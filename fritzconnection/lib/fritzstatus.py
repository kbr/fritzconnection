"""
Modul to read status-informations from an AVM FritzBox.
"""

import time

from ..core.exceptions import FritzServiceError
from .fritzbase import AbstractLibraryBase
from .fritztools import format_num, format_rate


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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # depending on the model (i.e. a repeater) some services
        # may not be available. Don't let FritzStatus crash at init.
        try:
            self.last_bytes_sent = self.bytes_sent
            self.last_bytes_received = self.bytes_received
        except FritzServiceError:
            pass
        self.last_traffic_call = time.time()

    @property
    def is_linked(self):
        """
        A boolean whether the FritzBox is physically linked to
        the provider.
        """
        status = self.fc.call_action('WANCommonIFC',
                                     'GetCommonLinkProperties')
        return status['NewPhysicalLinkStatus'] == 'Up'

    @property
    def is_connected(self):
        """
        A boolean whether the FritzBox has established an
        internet-connection.
        """
        status = self.fc.call_action('WANIPConn', 'GetStatusInfo')
        return status['NewConnectionStatus'] == 'Connected'

    @property
    def external_ip(self):
        """The external v4 ip-address."""
        return self.fc.call_action('WANIPConn',
            'GetExternalIPAddress')['NewExternalIPAddress']

    @property
    def external_ipv6(self):
        """The external v6 ip-address."""
        return self.fc.call_action('WANIPConn',
            'X_AVM_DE_GetExternalIPv6Address')['NewExternalIPv6Address']

    @property
    def uptime(self):
        """Uptime in seconds."""
        status = self.fc.call_action('WANIPConn', 'GetStatusInfo')
        return status['NewUptime']

    @property
    def str_uptime(self):
        """Uptime in seconds and in human readable format."""
        mins, secs = divmod(self.uptime, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02d' % (hours, mins, secs)

    @property
    def bytes_sent(self):
        """Total number of send bytes."""
        status = self.fc.call_action('WANCommonIFC',
                                     'GetTotalBytesSent')
        return status['NewTotalBytesSent']

    @property
    def bytes_received(self):
        """Total number of received bytes."""
        status = self.fc.call_action('WANCommonIFC',
                                     'GetTotalBytesReceived')
        return status['NewTotalBytesReceived']

    @property
    def transmission_rate(self):
        """
        The upstream and downstream values as a tuple in bytes per
        second. Use this for periodical calling.
        """
        sent = self.bytes_sent
        received = self.bytes_received
        traffic_call = time.time()
        time_delta = traffic_call - self.last_traffic_call
        upstream = int(1.0 * (sent - self.last_bytes_sent)/time_delta)
        downstream = int(1.0 * (received - self.last_bytes_received)/time_delta)
        self.last_bytes_sent = sent
        self.last_bytes_received = received
        self.last_traffic_call = traffic_call
        return upstream, downstream

    @property
    def str_transmission_rate(self):
        """
        Tuple of human readable transmission rate in bytes. First item
        is upstream, second item downstream.
        """
        upstream, downstream = self.transmission_rate
        return (
            format_num(upstream),
            format_num(downstream)
        )

    @property
    def max_linked_bit_rate(self):
        """
        Tuple with the maximun upstream- and downstream-rate
        of the physical link. The rate is given in bits/sec.
        """
        return self._get_max_bit_rate('WANCommonInterfaceConfig')

    @property
    def max_bit_rate(self):
        """
        Tuple with the maximun upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        return self._get_max_bit_rate('WANCommonIFC')

    def _get_max_bit_rate(self, servicename):
        """
        internal method to get the upstream and downstream-rates for
        different services of the WANCommonInterfaceConfig1 ServiceType.
        """
        status = self.fc.call_action(servicename, 'GetCommonLinkProperties')
        downstream = status['NewLayer1DownstreamMaxBitRate']
        upstream = status['NewLayer1UpstreamMaxBitRate']
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
            format_rate(upstream, unit='bits'),
            format_rate(downstream, unit ='bits')
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
            format_rate(upstream, unit='bits'),
            format_rate(downstream, unit ='bits')
        )

    def reconnect(self):
        """Makes a reconnection with a new external ip."""
        self.fc.reconnect()
