"""
fritzstatus.py

Module to inspect the FritzBox API for available services and actions.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..core.exceptions import FritzServiceError, FritzActionError
from ..lib.fritzstatus import FritzStatus
from . utils import get_cli_arguments, get_instance, print_header


def print_status(fs):
    print('FritzStatus:\n')
    status_informations = [
        ('is linked', 'is_linked'),
        ('is connected', 'is_connected'),
        ('external ip (v4)', 'external_ip'),
        ('external ip (v6)', 'external_ipv6'),
        ('uptime', 'str_uptime'),
        ('bytes send', 'bytes_sent'),
        ('bytes received', 'bytes_received'),
        ('max. bit rate', 'str_max_bit_rate'),
    ]
    for status, attribute in status_informations:
        try:
            information = getattr(fs, attribute)
        except (FritzServiceError, FritzActionError):
            information = f'unsupported attribute "{attribute}"'
        print(f'    {status:20}: {information}')
    print()


def main():
    args = get_cli_arguments()
    if not args.password:
        print('Exit: password required.')
    else:
        fs = get_instance(FritzStatus, args)
        print_header(fs)
        print_status(fs)


if __name__ == '__main__':
    main()
