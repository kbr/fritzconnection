"""
fritzwol.py

Module to wake up a single host via the Fritzbox built-in mechanism.
This can be helpful if the host to be woken up is in a different
broadcast domain/ subnet than the client which tries to wake up.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Authors: Maik Töpfer, Chris Bräucker
"""

from fritzconnection.core.exceptions import FritzArgumentError, FritzArrayIndexError, FritzAuthorizationError, FritzLookUpError
from ..lib.fritzhosts import FritzHosts
from . utils import (
    get_cli_arguments,
    get_instance,
    print_header,
    print_common_exception_message
)

class DeviceUnknownException(Exception):
    """Exception raised if the reference to the host does not resolve."""


def wake_host(fh, args):
    """
    Either wakes a host directly by MAC address, which should even work for hosts not known.
    Or it tries to find the given parameter in the device list to determine the MAC address.
    """
    mac = args.host

    if args.field == 'n':
        try:
            host = fh.get_generic_host_entry(int(args.host) - 1)
        except (FritzArgumentError, FritzArrayIndexError) as err:
            raise DeviceUnknownException("The index provided is invalid", args.host)
        mac = host['NewMACAddress']

    elif args.field == 'ip':
        try:
            host = fh.get_specific_host_entry_by_ip(args.host)
        except (FritzArgumentError, FritzLookUpError) as err:
            raise DeviceUnknownException("The IP provided is unknown", args.host)
        mac = host['NewMACAddress']

    elif args.field == 'name':
        found = False
        for entry in fh.get_generic_host_entries():
            if entry['NewHostName'].lower() == args.host.lower():
                mac = entry['NewMACAddress']
                found = True
                break

        if not found:
            raise DeviceUnknownException("The hostname provided is unknown", args.host)

    fh.wakeonlan_host(mac)
    print(f"Waking {mac}")



def add_arguments(parser):
    parser.add_argument('field',
                        choices=('ip', 'name', 'mac', 'n'),
                        default='mac',
                        nargs='?',
                        help='Which host field to wake by. ' +
                        'Retrieve this data with the `fritzhosts` command. ' +
                        '\'mac\' sends the WoL package directly, without checking. ' +
                        '(default: mac)')
    parser.add_argument('host', help='Field value of host to be woken up')


def execute():
    arguments = get_cli_arguments(add_arguments)
    fh = get_instance(FritzHosts, arguments)
    print_header(fh)
    wake_host(fh, arguments)


def main():
    try:
        execute()
    except FritzAuthorizationError as err:
        print_common_exception_message(err)
    except FritzArgumentError:
        print(f"Error: Invalid MAC address format")
    except DeviceUnknownException as err:
        print(f"Error: {err.args[0]}: {err.args[1]}")


if __name__ == '__main__':
    main()
