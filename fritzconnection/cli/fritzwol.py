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

class WakeOnLanException(Exception):
    """
    Exception raised when encountering issues while attempting to start a device using "Wake on LAN" (WoL).
    """
    pass

class WakeOnLan:
    """
    This class provides access to the "Start computer" (German "Computer starten") feature of a host via the command line.
    This enables waking up computers in the local network which are on a different broadcast domain/ subnet.
    """
    def __init__(self, fc, fh):
        self.fc = fc
        self.fh = fh

    def wakeup(self, host_name):
        """
        Wake up the provided local computer.

        Raises:
            WakeOnLanException: If the hostname is unknown at the Fritzbox or if there was an error sending the WoL command
        """
        mac = self._get_mac_address(host_name)
        self._wakeup_host(mac)

    def _get_mac_address(self, host_name):
        for host in self.fh.get_hosts_info(): 
            if host["name"] == host_name: 
                return host["mac"]
        raise WakeOnLanException(
                f"Host '{host_name}' is unknown at Fritzbox.")

    def _wakeup_host(self, mac):
        try:
            self.fc.call_action(
                'Hosts1',
                'X_AVM-DE_WakeOnLANByMACAddress',
                NewMACAddress=mac)
        except FritzConnectionException as e:
            raise WakeOnLanException(f"Error sending Wake on LAN command: {e}")


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
            wol = WakeOnLan(fc, FritzHosts(fc))
            print(f"Waking up host '{args.host}'...")
            wol.wakeup(args.host)
            print("Done")

        except WakeOnLanException as e:
            print(e)


if __name__ == '__main__':
    main()
