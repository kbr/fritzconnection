"""
fritzhosts.py

Module to inspect the FritzBox API for registered hosts.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..core.exceptions import FritzAuthorizationError
from ..lib.fritzhosts import FritzHosts
from .utils import (
    get_cli_arguments,
    get_instance,
    print_header,
    print_common_exception_message
)


def print_status(fh):
    print('FritzHosts:')
    print('List of registered hosts:\n')
    print('{:>3}: {:<16} {:<28} {:<17}   {}\n'.format(
        'n', 'ip', 'name', 'mac', 'status'))
    hosts = fh.get_hosts_info()
    for index, host in enumerate(hosts, start=1):
        status = 'active' if host['status'] else  '-'
        ip = host['ip'] if host['ip'] else '-'
        mac = host['mac'] if host['mac'] else '-'
        hn = host['name']
        print(f'{index:>3}: {ip:<16} {hn:<28} {mac:<17}   {status}')
    print('\n')


def execute():
    args = get_cli_arguments()
    fh = get_instance(FritzHosts, args)
    print_header(fh)
    print_status(fh)


def main():
    try:
        execute()
    except FritzAuthorizationError as err:
        print_common_exception_message(err)


if __name__ == '__main__':
    main()
