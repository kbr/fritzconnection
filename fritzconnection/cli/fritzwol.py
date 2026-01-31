"""
fritzwol.py

Module to wake up a single host via the Fritzbox built-in mechanism.
This can be helpful if the host to be woken up is in a different
broadcast domain/subnet than the client which tries to wake up.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Authors: Maik Töpfer, Chris Bräucker
"""

from fritzconnection.core.exceptions import (
    FritzArgumentError,
    FritzAuthorizationError,
    FritzLookUpError,
)

from ..lib.fritzhosts import FritzHosts
from .utils import (
    get_cli_arguments,
    get_instance,
    print_common_exception_message,
    print_header,
)


def wake_host(fh, args):
    """
    Either wakes a host directly by MAC address, which should even work for hosts not known.
    Or it tries to find the given parameter in the device list to determine the MAC address.
    """

    print(args)

    if args.device_mac_address:
        mac = args.device_mac_address

    elif args.device_ip_address:
        try:
            host = fh.get_specific_host_entry_by_ip(args.device_ip_address)
        except (FritzArgumentError, FritzLookUpError):
            msg = f"Error: unknown IP {args.device_ip_address}"
            raise FritzArgumentError(msg)
        mac = host['NewMACAddress']

    elif args.device_name:
        device_name = args.device_name.lower()
        for entry in fh.get_generic_host_entries():
            if entry['NewHostName'].lower() == device_name:
                mac = entry['NewMACAddress']
                break
        else:
            msg = f"Error: unknown device name '{args.device_name}'"
            raise FritzArgumentError(msg)

    fh.wakeonlan_host(mac)
    print(f"Waking {mac}")


def add_arguments(parser):
    arggroup = parser.add_argument_group('Wake-on-LAN options', 'mutually exclusive arguments to reference the target host')
    group = arggroup.add_mutually_exclusive_group(required=True)
    group.add_argument('-m', '--device-mac',
                        dest='device_mac_address',
                        default=None,
                        help='MAC address of the device to wake up. Sends a WoL packet without checking device existence.'
    )
    group.add_argument('-I', '--device-ip',
                        dest='device_ip_address',
                        default=None,
                        help='IP address of the device to wake up. Checks against the list of known devices.'
    )
    group.add_argument('-n', '--device-name',
                        dest='device_name',
                        default=None,
                        help='Name of the device to wake up. Checks against the list of known devices.'
    )


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
    except FritzArgumentError as err:
        print(err)


if __name__ == '__main__':
    main()
