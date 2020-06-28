"""
fritzcall.py

Module to inspect the FritzBox phone API.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..lib.fritzcall import FritzCall
from . utils import get_cli_arguments, get_instance, print_header


def report_calls(fc, arguments):
    print('FritzCall:')
    days = arguments.days
    num = arguments.num if not days else None
    if arguments.type == 'in':
        calls = fc.get_received_calls(num=num, days=days)
    elif arguments.type == 'out':
        calls = fc.get_out_calls(num=num, days=days)
    elif arguments.type == 'missed':
        calls = fc.get_missed_calls(num=num, days=days)
    else:
        calls = fc.get_calls(num=num, days=days)
    call_type = arguments.type if arguments.type else 'all'
    print('List of calls:', call_type, '\n')
    type_ = 'type'
    number = 'number'
    time = 'date/time'
    duration = 'duration'
    print(f'{type_:>6}   {number:24}{time:>18}{duration:>12}\n')
    for call in calls:
        print(call)
    print()


def dial_number(fc, number):
    print(f'dialing number: {number}')
    fc.dial(number)
    print('dialing done, please wait for signal.')


def add_arguments(parser):
    parser.add_argument('-n', '--num',
                        nargs='?', default=None, const=None,
                        help='max number of calls in the call-list')
    parser.add_argument('-d', '--days',
                        nargs='?', default=None, const=None,
                        help='number of days to look back for calls.')
    parser.add_argument('-t', '--type',
                        nargs='?', default=None, const=None,
                        help='type of calls: [in|out|missed]')
    parser.add_argument('-c', '--call',
                        nargs='?', default=None, const=None,
                        help='phone number to call')


def main():
    arguments = get_cli_arguments(add_arguments)
    if not arguments.password:
        print('Exit: password required.')
        return
    fc = get_instance(FritzCall, arguments)
    if arguments.call:
        dial_number(fc, arguments.call)
    else:
        print_header(fc)
        report_calls(fc, arguments)


if __name__ == '__main__':
    main()
