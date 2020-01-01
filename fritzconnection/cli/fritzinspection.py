"""
fritzinspection.py

Module to inspect the FritzBox API for available services and actions.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""


import argparse
import os

from ..core.exceptions import FritzConnectionException
from ..core.fritzconnection import (
    FritzConnection,
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
)
from .. import package_version


class FritzInspection:
    """
    Class for cli use to inspect available services and according
    actions of the given device (the Fritz!Box).
    """
    # pylint: disable=invalid-name  # self.fc is ok.

    def __init__(self, address, port, user, password, use_tls):
        self.fc = FritzConnection(address=address,
                                  port=port,
                                  user=user,
                                  password=password,
                                  use_tls=use_tls)

    def view_header(self):
        print(self.fc)

    def view_servicenames(self):
        """Send all known service names to stdout."""
        print('Servicenames:')
        for service_name in self.fc.services:
            print('{:20}{}'.format('', service_name))

    def view_actionnames(self, service_name, view_arguments=False):
        """Send all action names of the given service to stdout."""
        print('\n{:<20}{}'.format('Servicename:', service_name))
        print('Actionnames:')
        try:
            service = self.fc.services[service_name]
        except KeyError as err:
            print(f'Error: Invalid Servicename {err}')
        else:
            for action_name in service.actions:
                print('{:20}{}'.format('', action_name))
                if view_arguments:
                    action = service.actions[action_name]
                    for argument in sorted(action.arguments.keys()):
                        print('{:24}- {}'.format('', argument))
                    print()


    def view_actionarguments(self, service_name, action_name):
        """Send all action names of the given service to stdout."""
        try:
            service = self.fc.services[service_name]
        except KeyError as err:
            print(f'Error: Invalid Servicename {err}')
            return
        try:
            action = service.actions[action_name]
        except KeyError as err:
            print(f'Error: Invalid Actionname {err}')
            return
        print('\n{:<20}{}'.format('Service:', service_name))
        print('{:<20}{}'.format('Action:', action_name))
        print('Parameters:\n')
        print('    {:30}{:14}{}\n'.format('Name', 'direction', 'data type'))
        for argument in action.arguments.values():
            if argument.direction == 'in':
                direction = '-> in'
            else:
                direction = '   out ->'
            var = service.state_variables.get(argument.relatedStateVariable, '')
            line = f'    {argument.name:30}{direction:14}{var.dataType}'
            print(line)


def get_cli_arguments():
    """
    Returns a NameSpace object from the ArgumentParser parsing the given
    command line arguments.
    """
    print(f'\nFritzConnection v{package_version}')
    parser = argparse.ArgumentParser(description='Fritz!Box API Inspection:')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=FRITZ_IP_ADDRESS, const=None,
                        dest='address',
                        help='Specify ip-address of the FritzBox to connect to.'
                             'Default: %s' % FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        help='Port of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs='?', default=os.getenv('FRITZ_USERNAME', None),
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=os.getenv('FRITZ_PASSWORD', None),
                        help='Fritzbox authentication password')
    parser.add_argument('-r', '--reconnect',
                        action='store_true',
                        help='Reconnect and get a new ip')
    parser.add_argument('-s', '--services',
                        action='store_true',
                        help='List all available services')
    parser.add_argument('-S', '--serviceactions',
                        nargs=1,
                        help='List actions for the given service: <service>')
    parser.add_argument('-a', '--servicearguments',
                        nargs=1,
                        help='List arguments for the actions of a '
                             'specified service: <service>.')
    parser.add_argument('-A', '--actionarguments',
                        nargs=2,
                        help='List arguments for the given action of a '
                             'specified service: <service> <action>. '
                             'Lists also direction and data type of the '
                             'arguments.')
    parser.add_argument('-e', '--encrypt',
                        nargs='?', default=False, const=True,
                        help='use secure connection')
    args = parser.parse_args()
    return args


def get_inspector(args):
    try:
        inspector = FritzInspection(
            address=args.address,
            port=args.port,
            user=args.username,
            password=args.password,
            use_tls=args.encrypt)
    except FritzConnectionException as err:
        return None
    return inspector


def run_inspector(inspector, args):
    inspector.view_header()
    if args.services:
        inspector.view_servicenames()
    elif args.serviceactions:
        inspector.view_actionnames(args.serviceactions[0])
    elif args.servicearguments:
        inspector.view_actionnames(args.servicearguments[0], view_arguments=True)
    elif args.actionarguments:
        inspector.view_actionarguments(args.actionarguments[0],
                                       args.actionarguments[1])
    elif args.reconnect:
        inspector.fc.reconnect()
        print('reconnect the router.')


def main():
    """CLI entry point."""
    args = get_cli_arguments()
    inspector = get_inspector(args)
    if inspector:
        run_inspector(inspector, args)
    print() # print an empty line


if __name__ == '__main__':
    main()
