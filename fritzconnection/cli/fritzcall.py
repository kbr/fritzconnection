
import argparse

from .. import package_version
from ..core.fritzconnection import (
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
)
from ..lib.fritzcall import FritzCall


def get_fritzcall(arguments):
    return FritzCall(address=arguments.address,
                     port=arguments.port,
                     user=arguments.username,
                     password=arguments.password,
                     use_tls=arguments.encrypt)


def report_calls(fc, arguments):
    print(f'\nFritzConnection v{package_version}')
    print(fc.fc)
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
    print('\nList of calls:', call_type, '\n')
    type_ = 'type'
    number = 'number'
    time = 'date/time'
    duration = 'duration'
    print(f'{type_:>6}   {number:24}{time:>18}{duration:>12}\n')
    for call in calls:
        print(call)


def dial_number(fc, number):
    print(f'dialing number: {number}')
    fc.dial(number)
    print('dialing done, please wait for signal.')


def get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Callhistory')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=None, const=None,
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication password')
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
    parser.add_argument('-e', '--encrypt',
                        nargs='?', default=False, const=True,
                        help='use secure connection')
    args = parser.parse_args()
    return args


def main():
    arguments = get_cli_arguments()
    if not arguments.password:
        print('Exit: password required.')
        return
    fc = get_fritzcall(arguments)
    if arguments.call:
        dial_number(fc, arguments.call)
    else:
        report_calls(fc, arguments)


if __name__ == '__main__':
    main()
