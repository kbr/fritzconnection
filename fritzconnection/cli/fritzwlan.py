"""
fritzwlan.py

Module to inspect the FritzBox API for wlan devices.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

import itertools

from ..core.exceptions import FritzServiceError, FritzAuthorizationError
from ..lib.fritzwlan import FritzWLAN, SERVICE
from . utils import (
    get_cli_arguments,
    get_instance,
    print_header,
    print_common_exception_message
)


def get_header():
    index = 'index'
    status = 'active'
    mac = 'mac'
    ip = 'ip'
    signal = 'signal'
    speed = 'speed'
    return f'{index:>5}{status:>8}{mac:>20}{ip:>18}{signal:>8}{speed:>8}'


def report_wlanconfiguration(fw, extension):
    fw.service = extension
    hosts_info = fw.get_hosts_info()
    if hosts_info:
        print(f'Hosts registered at {SERVICE}{extension}:')
        print(f'WLAN name: {fw.ssid}')
        print(f'channel  : {fw.channel}')
        print(get_header())
        for info in hosts_info:
            index = info['index']
            status = info['status']
            mac = info['mac']
            ip = info['ip']
            signal = info['signal']
            speed = info['speed']
            print(f'{index:>5}{status:>8}{mac:>20}{ip:>18}{signal:>8}{speed:>8}')
        print()


def report_devices(fw, args):
    if args.service:
        try:
            report_wlanconfiguration(fw, args.service)
        except FritzServiceError as err:
            print(f'Error: {err}')
    else:
        for n in itertools.count(1):
            try:
                report_wlanconfiguration(fw, n)
            except FritzServiceError:
                break


def add_arguments(parser):
    parser.add_argument('-s', '--service',
                        nargs='?', default=0, const=None,
                        help='WLANConfiguration service number')


def execute():
    arguments = get_cli_arguments(add_arguments)
    fritz_wlan = get_instance(FritzWLAN, arguments)
    print_header(fritz_wlan)
    report_devices(fritz_wlan, arguments)


def main():
    try:
        execute()
    except FritzAuthorizationError as err:
        print_common_exception_message(err)


if __name__ == '__main__':
    main()
