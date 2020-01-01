
import argparse

from .. import package_version
from ..lib.fritzhomeauto import FritzHomeAutomation
from ..core.fritzconnection import (
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
)


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


def report_status(fh, arguments):
    print(f'\nFritzConnection v{package_version}')
    print(fh.fc)
    print('Status of registered home-automation devices:\n')
    if arguments.verbose:
        report_verbose(fh)
    else:
        report_compact(fh)


def switch_device(fh, arguments):
    ain = arguments.switch[0]
    state = arguments.switch[1].lower() == 'on'
    fh.set_switch(identifier=ain, on=state)


def get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox HomeAuto')
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
    parser.add_argument('-v', '--verbose',
                        nargs='?', default=False, const=True,
                        help='report in verbose mode')
    parser.add_argument('-s', '--switch',
                        nargs=2,
                        help='set switch state. requires two parameters: '
                             'ain and state [on|off]')
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
    fh = FritzHomeAutomation(address=arguments.address,
                             port=arguments.port,
                             user=arguments.username,
                             password=arguments.password,
                             use_tls=arguments.encrypt)
    if arguments.switch:
        switch_device(fh, arguments)
    else:
        report_status(fh, arguments)


if __name__ == '__main__':
    main()
