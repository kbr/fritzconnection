#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
fritzstatus.py

Modul to read status-informations from an AVM FritzBox.

License: MIT https://opensource.org/licenses/MIT
Source: https://github.com/kbr/fritzconnection
Author: Klaus Bremer
"""

import argparse
import collections
import os
import time

# tiny hack to run this as a package but also from the command line. In
# the latter case ValueError is raised from python 2.7 and SystemError
# from Python 3.5 and ImportError from Python 3.6
try:
    from . import fritzconnection
    from . import fritztools
except (ValueError, SystemError, ImportError):
    import fritzconnection
    import fritztools


# version-access:
def get_version():
    return fritzconnection.get_version()


class FritzStatus(object):
    """
    Class for requesting status-informations:
    up, down, ip, activity (bytes per second send/received)
    Every property will raise an IOError if the connection
    with the FritzBox fails.

    Keep in mind, that FritzBoxes may return different informations
    about the status depending whether this service gets called with or
    without a password.
    """

    def __init__(self, fc=None, address=None, port=None,
                       user=None, password=None):
        super(FritzStatus, self).__init__()
        if fc is None:
            fc = fritzconnection.FritzConnection(
                address=address,
                port=port,
                user=user,
                password=password,
            )
        self.fc = fc
        self.last_bytes_sent = self.bytes_sent
        self.last_bytes_received = self.bytes_received
        self.last_traffic_call = time.time()

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def is_linked(self):
        """Returns True if the FritzBox is physically linked to the provider."""
        status = self.fc.call_action('WANCommonIFC',
                                     'GetCommonLinkProperties')
        return status['NewPhysicalLinkStatus'] == 'Up'

    @property
    def is_connected(self):
        """
        Returns True if the FritzBox has established an internet-connection.
        """
        status = self.fc.call_action('WANIPConn', 'GetStatusInfo')
        return status['NewConnectionStatus'] == 'Connected'

    @property
    def wan_access_type(self):
        """Returns connection-type: DSL, Cable."""
        return self.fc.call_action('WANCommonIFC',
            'GetCommonLinkProperties')['NewWANAccessType']

    @property
    def external_ip(self):
        """Returns the external ip-address."""
        return self.fc.call_action('WANIPConn',
            'GetExternalIPAddress')['NewExternalIPAddress']

    @property
    def external_ipv6(self):
        """Returns the external ip-address."""
        return self.fc.call_action('WANIPConn',
            'X_AVM_DE_GetExternalIPv6Address')['NewExternalIPv6Address']

    @property
    def uptime(self):
        """uptime in seconds."""
        status = self.fc.call_action('WANIPConn', 'GetStatusInfo')
        return status['NewUptime']

    @property
    def str_uptime(self):
        """uptime in human readable format."""
        mins, secs = divmod(self.uptime, 60)
        hours, mins = divmod(mins, 60)
        return '%02d:%02d:%02d' % (hours, mins, secs)

    @property
    def bytes_sent(self):
        status = self.fc.call_action('WANCommonIFC',
                                     'GetTotalBytesSent')
        return status['NewTotalBytesSent']

    @property
    def bytes_received(self):
        status = self.fc.call_action('WANCommonIFC',
                                     'GetTotalBytesReceived')
        return status['NewTotalBytesReceived']

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
        upstream = int(1.0 * (sent - self.last_bytes_sent)/time_delta)
        downstream = int(1.0 * (received - self.last_bytes_received)/time_delta)
        self.last_bytes_sent = sent
        self.last_bytes_received = received
        self.last_traffic_call = traffic_call
        return upstream, downstream

    @property
    def str_transmission_rate(self):
        """Returns a tuple of human readable transmission rates in bytes."""
        upstream, downstream = self.transmission_rate
        return (
            fritztools.format_num(upstream),
            fritztools.format_num(downstream)
        )

    @property
    def max_linked_bit_rate(self):
        """
        Returns a tuple with the maximun upstream- and downstream-rate
        of the physical link. The rate is given in bits/sec.
        """
        return self._get_max_bit_rate('WANCommonInterfaceConfig')

    @property
    def max_bit_rate(self):
        """
        Returns a tuple with the maximun upstream- and downstream-rate
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
        Same as max_bit_rate but returns the rate in bytes/sec.
        """
        upstream, downstream = self.max_bit_rate
        return upstream / 8.0, downstream / 8.0

    @property
    def str_max_linked_bit_rate(self):
        """
        Returns a human readable maximun upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        upstream, downstream = self.max_linked_bit_rate
        return (
            fritztools.format_rate(upstream, unit='bits'),
            fritztools.format_rate(downstream, unit ='bits')
        )

    @property
    def str_max_bit_rate(self):
        """
        Returns a human readable maximun upstream- and downstream-rate
        of the given connection. The rate is given in bits/sec.
        """
        upstream, downstream = self.max_bit_rate
        return (
            fritztools.format_rate(upstream, unit='bits'),
            fritztools.format_rate(downstream, unit ='bits')
        )

    def reconnect(self):
        """Makes a reconnection with a new external ip."""
        self.fc.reconnect()


# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def print_status(address=None, port=None, user=None, password=None):
    print('\nFritzStatus:')
    print('{:<22}{}'.format('version:', get_version()))
    fs = FritzStatus(address=address, port=port, user=user, password=password)
    status_informations = collections.OrderedDict([
        ('model:', fs.modelname),
        ('is linked:', fs.is_linked),
        ('is connected:', fs.is_connected),
        ('external ip:', fs.external_ip),
        ('uptime:', fs.str_uptime),
        ('bytes send:', fs.bytes_sent),
        ('bytes received:', fs.bytes_received),
        ('max. bit rate:', fs.str_max_bit_rate),
        ])
    try:
        information = fs.str_max_linked_bit_rate
    except fritzconnection.ServiceError:
        information = 'password required for information'
    except fritzconnection.AuthorizationError as err:
        information = str(err)
    status_informations['max. linked bit rate:'] = information
    for status, information in status_informations.items():
        print('{:<22}{}'.format(status, information))


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Status')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=None, const=None,
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_IP_ADDRESS)
    parser.add_argument('-u', '--username',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication password')
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_TCP_PORT)
    args = parser.parse_args()
    return args


def _print_status(arguments):
    print_status(
        address=arguments.address,
        port=arguments.port,
        user=arguments.username,
        password=arguments.password,
    )

def main():
    _print_status(_get_cli_arguments())

if __name__ == '__main__':
    main()
