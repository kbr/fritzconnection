"""
fritzhosts.py

Module to inspect the FritzBox API for registered hosts.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..lib.fritzhosts import FritzHosts
from . utils import get_cli_arguments, get_instance, print_header


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


def main():
    args = get_cli_arguments()
    if not args.password:
        print('Exit: password required.')
    else:
        fh = get_instance(FritzHosts, args)
        print_header(fh)
        print_status(fh)


if __name__ == '__main__':
    main()
