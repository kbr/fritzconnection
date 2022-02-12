"""
fritzwol.py

Module to wake up a single host via the Fritzbox built-in mechanism.
This can be helpful if the host to be woken up is in a different
broadcast domain/ subnet than the client which tries to wake up.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Maik Töpfer
"""

from fritzconnection.core.exceptions import FritzConnectionException
from fritzconnection.core.fritzconnection import FritzConnection
from ..lib.fritzhosts import FritzHosts
from . utils import get_cli_arguments, get_instance, print_header


class WakeOnLan:
    def __init__(self, fc, fh):
        self._fc = fc
        self._fh = fh

    def wakeup(self, host_name):
        print(f"Waking up host '{host_name}'...")
        mac = self._get_mac_address(host_name)
        self._wakeup_host(mac)
        print("Done")

    def _get_mac_address(self, host_name):
        mac = [host['mac']
               for host in self._fh.get_hosts_info() if host['name'] == host_name]
        if not mac:
            raise WakeOnLanException(
                f"Host '{host_name}' is unknown at Fritzbox.")
        return mac[0]

    def _wakeup_host(self, mac):
        try:
            self._fc.call_action(
                'Hosts1',
                'X_AVM-DE_WakeOnLANByMACAddress',
                NewMACAddress=mac)
        except FritzConnectionException as e:
            raise WakeOnLanException(f"Error sending Wake on LAN command: {e}")


class WakeOnLanException(Exception):
    pass


def _add_arguments(parser):
    parser.add_argument('host', help='name of host to be woken up')


def main():
    args = get_cli_arguments(_add_arguments)
    if not args.password:
        print('Exit: password required.')
    else:
        fc = get_instance(FritzConnection, args)
        print_header(fc)
        try:
            WakeOnLan(fc, FritzHosts(fc)).wakeup(args.host)
        except WakeOnLanException as e:
            print(e)
            exit(1)


if __name__ == '__main__':
    main()
