"""
fritzhomeauto.py

Module to inspect the FritzBox homeautomation API.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..lib.fritzhomeauto import FritzHomeAutomation
from . utils import get_cli_arguments, get_instance, print_header


def report_verbose(fh):
    informations = fh.device_informations()
    for info in informations:
        width = len(max(info.keys(), key=lambda x: len(x)))
        line = f'{{attribute:{width}}} : {{value}}'
        for attribute in sorted(info.keys()):
            print(line.format(attribute=attribute, value=info[attribute]))
        print()  # add blank line between devices


def report_compact(fh):
    name = 'Device Name'
    ain = 'AIN'
    power = 'Power[W]'
    temperature = 't[°C]'
    switch_state = 'switch'
    print(f'{name:24}{ain:18}{power:>10}{temperature:>8}   {switch_state}')
    for di in fh.device_informations():
        name = di['NewDeviceName']
        ain = di['NewAIN']
        ain = f"'{ain}'"
        power = di['NewMultimeterPower'] * 0.01
        temperature = di['NewTemperatureCelsius'] *0.1
        switch_state = di['NewSwitchState'].lower()
        print(f'{name:24}{ain:18}{power:>10.3f}{temperature:>8.1f}   {switch_state}')
    print()


def report_status(fh, arguments):
    print('FritzHomeautomation:')
    print('Status of registered home-automation devices:\n')
    if arguments.verbose:
        report_verbose(fh)
    else:
        report_compact(fh)


def switch_device(fh, arguments):
    ain = arguments.switch[0]
    state = arguments.switch[1].lower() == 'on'
    fh.set_switch(identifier=ain, on=state)


def add_arguments(parser):
    parser.add_argument('-v', '--verbose',
                        nargs='?', default=False, const=True,
                        help='report in verbose mode')
    parser.add_argument('-s', '--switch',
                        nargs=2,
                        help='set switch state. requires two parameters: '
                             'ain and state [on|off]')


def main():
    arguments = get_cli_arguments(add_arguments)
    if not arguments.password:
        print('Exit: password required.')
        return
    fh = get_instance(FritzHomeAutomation, arguments)
    if arguments.switch:
        switch_device(fh, arguments)
    else:
        print_header(fh)
        report_status(fh, arguments)


if __name__ == '__main__':
    main()
