#! /opt/local/bin/python2.7
#! /usr/bin/env python2.7


import time
import fritzconnection
import fritztools


class FritzStatus(object):
    """
    Class for requsting status-informations:
    up, down, ip, activity (bytes per second send/received)
    Every property will raise an IOError if the connection
    with the FritzBox fails.
    """

    def __init__(self, address=fritzconnection.FRITZ_ADDRESS,
                       port=fritzconnection.FRITZ_TCP_PORT):
        super(FritzStatus, self).__init__()
        self.fc = fritzconnection.FritzConnection(address=address, port=port)
        self.last_bytes_sent = self.bytes_sent
        self.last_bytes_received = self.bytes_received
        self.last_traffic_call = time.time()

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def is_linked(self):
        """Returns True if the FritzBox is physically linked to the provider."""
        status = self.fc.call_action('GetCommonLinkProperties')
        return status['NewPhysicalLinkStatus'] == 'Up'

    @property
    def is_connected(self):
        """
        Returns True if the FritzBox has established an internet-connection.
        """
        status = self.fc.call_action('GetStatusInfo')
        return status['NewConnectionStatus'] == 'Connected'

    @property
    def wan_access_type(self):
        """Returns connection-type: DSL, Cable."""
        return self.fc.call_action(
            'GetCommonLinkProperties')['NewWANAccessType']

    @property
    def external_ip(self):
        """Returns the external ip-address."""
        return self.fc.call_action(
            'GetExternalIPAddress')['NewExternalIPAddress']

    @property
    def uptime(self):
        """uptime in seconds."""
        return self.fc.call_action('GetStatusInfo')['NewUptime']

    @property
    def str_uptime(self):
        """uptime in human readable format."""
        mins, secs = divmod(self.uptime, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02d' % (hours, mins, secs)

    @property
    def bytes_sent(self):
        return self.fc.call_action('GetTotalBytesSent')['NewTotalBytesSent']

    @property
    def bytes_received(self):
        return self.fc.call_action(
            'GetTotalBytesReceived')['NewTotalBytesReceived']

    @property
    def transmission_rate(self):
        """
        Returns the upstream, downstream values as a tuple in bytes per
        second. Use this for periodical calling.
        """
        sent = self.bytes_sent
        received = self.bytes_received
        traffic_call = time.time()
        time_delta = traffic_call - self.last_traffic_call
        upstream = int(1.0 * (sent - self.last_bytes_sent) / time_delta)
        downstream = int(1.0 * (received - self.last_bytes_received) / time_delta)
        self.last_bytes_sent = sent
        self.last_bytes_received = received
        self.last_traffic_call = traffic_call
        return upstream, downstream

    @property
    def str_transmission_rate(self):
        """Returns a tuple of human readable transmission rates in bytes."""
        upstream, downstream = self.transmission_rate
        return self.format_num(upstream), self.format_num(downstream)

    @property
    def max_bit_rate(self):
        """
        Returns a tuple with the maximun upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        stream_rate = self.fc.call_action('GetCommonLinkProperties')
        downstream = stream_rate['NewLayer1DownstreamMaxBitRate']
        upstream = stream_rate['NewLayer1UpstreamMaxBitRate']
        return upstream, downstream

    @property
    def max_byte_rate(self):
        """
        Same as max_bit_rate but returns the rate in bytes/sec.
        """
        upstream, downstream = self.max_bit_rate
        return upstream / 8, downstream / 8

    @property
    def str_max_bit_rate(self):
        """
        Returns a human readable maximun upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        upstream, downstream = self.max_bit_rate
        return fritztools.format_rate(upstream, unit='bits'), \
               fritztools.format_rate(downstream, unit ='bits')

    def reconnect(self):
        """Makes a reconnection with a new external ip."""
        self.fc.reconnect()


if __name__ == '__main__':
    fs = FritzStatus()
    print(fs.modelname)
    print(fs.bytes_sent)
    print(fs.bytes_received)
    print(fs.is_linked)
    print(fs.is_connected)
    print(fs.external_ip)
    print(fs.uptime)
    print(fs.str_uptime)
    print(fs.max_bit_rate)
    print(fs.max_byte_rate)
    print(fs.str_max_bit_rate)
    print(fs.transmission_rate)
    time.sleep(1)
    print(fs.transmission_rate)

