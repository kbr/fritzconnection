"""
fritzinspection.py

Module to inspect the FritzBox API for available services and actions.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

import datetime

from ..core.fritzconnection import FritzConnection
from . utils import get_cli_arguments, get_instance, print_header


class FritzInspection:
    """
    Class for cli use to inspect available services and according
    actions of the given device (the Fritz!Box).
    """
    # pylint: disable=invalid-name  # self.fc is ok.

    def __init__(self, fc):
        self.fc = fc

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
        print('    {:38}{:14}{}\n'.format('Name', 'direction', 'data type'))
        for argument in action.arguments.values():
            if argument.direction == 'in':
                direction = '-> in'
            else:
                direction = '   out ->'
            var = service.state_variables.get(argument.relatedStateVariable, '')
            line = f'    {argument.name:38}{direction:14}{var.dataType}'
            print(line)

    def view_complete_api(self):
        """
        Send the complete api to stdout.

        This can be a lengthy output that may be redirected to a file.
        """
        print()
        system_info = self.fc.device_manager.system_info
        print(
            f"system : {system_info[-1]}\n"
            f"build  : {system_info[-2]}\n"
            f"hw-code: {system_info[0]}"
        )
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Report date: {now}")
        for service_name, service in self.fc.services.items():
            if service_name == 'any1':
                continue
            print()
            print('=' * 65)
            for action_name in service.actions:
                self.view_actionarguments(service_name, action_name)


def add_arguments(parser):
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
    parser.add_argument('-c', '--complete',
                        nargs='?', default=False, const=True,
                        help='List the complete api of the router')


def run_inspector(inspector, args):
    print_header(inspector.fc)
    if args.services:
        inspector.view_servicenames()
    elif args.serviceactions:
        inspector.view_actionnames(args.serviceactions[0])
    elif args.servicearguments:
        inspector.view_actionnames(args.servicearguments[0], view_arguments=True)
    elif args.actionarguments:
        inspector.view_actionarguments(args.actionarguments[0],
                                       args.actionarguments[1])
    elif args.complete:
        inspector.view_complete_api()
    elif args.reconnect:
        inspector.fc.reconnect()
        print('reconnect the router.')
    print()


def main():
    """CLI entry point."""
    args = get_cli_arguments(add_arguments)
    fc = get_instance(FritzConnection, args)
    inspector = FritzInspection(fc=fc)
    run_inspector(inspector, args)


if __name__ == '__main__':
    main()
