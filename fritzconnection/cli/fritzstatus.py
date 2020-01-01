"""
fritzstatus.py

Module to inspect the FritzBox API for available services and actions.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

import argparse

from .. import package_version
from ..core.exceptions import (
    FritzServiceError,
    FritzActionError,
)
from ..core.fritzconnection import (
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
)
from ..lib.fritzstatus import FritzStatus


def print_status(address=None, port=None, user=None,
                 password=None, use_tls=False):
    print(f'\nFritzConnection v{package_version}')
    fs = FritzStatus(address=address,
                     port=port,
                     user=user,
                     password=password,
                     use_tls=use_tls)
    print(f'FritzStatus for {fs.fc}:\n')
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


def get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Status')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=None, const=None,
                        dest='address',
                        help=f'ip-address of the FritzBox to connect to. '
                             f'Default: {FRITZ_IP_ADDRESS}')
    parser.add_argument('-u', '--username',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication password')
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        dest='port',
                        help=f'port of the FritzBox to connect to. '
                             f'Default: {FRITZ_TCP_PORT}')
    parser.add_argument('-e', '--encrypt',
                        nargs='?', default=False, const=True,
                        help='use secure connection')
    args = parser.parse_args()
    return args


def main():
    args = get_cli_arguments()
    if not args.password:
        print('Exit: password required.')
    else:
        print_status(address=args.address,
                     port=args.port,
                     user=args.username,
                     password=args.password,
                     use_tls=args.encrypt)


if __name__ == '__main__':
    main()
