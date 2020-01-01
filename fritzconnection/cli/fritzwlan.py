
import argparse
import itertools

from ..lib.fritzwlan import (
    FritzWLAN,
    SERVICE,
)
from ..core.exceptions import FritzServiceError
from ..core.fritzconnection import (
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
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
    host_informations = fw.get_hosts_info()
    if host_informations:
        print(f'Hosts registered at {SERVICE}{extension}:')
        print(f'WLAN name: {fw.ssid}')
        print(f'channel  : {fw.channel}')
        print(get_header())
        for info in host_informations:
            index = info['index']
            status = info['status']
            mac = info['mac']
            ip = info['ip']
            signal = info['signal']
            speed = info['speed']
            print(f'{index:>5}{status:>8}{mac:>20}{ip:>18}{signal:>8}{speed:>8}')
        print()


def report_devices(arguments):
    fw = FritzWLAN(address=arguments.address,
                   port=arguments.port,
                   user=arguments.username,
                   password=arguments.password,
                   service=arguments.service,
                   use_tls=arguments.encrypt)
    print(fw.fc)
    if arguments.service:
        try:
            report_wlanconfiguration(fw, arguments.service)
        except FritzServiceError as err:
            print(f'Error: {err}')
    else:
        for n in itertools.count(1):
            try:
                report_wlanconfiguration(fw, n)
            except FritzServiceError:
                break


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
    parser.add_argument('-s', '--service',
                        nargs='?', default=0, const=None,
                        help='WLANConfiguration service number')
    parser.add_argument('-e', '--encrypt',
                        nargs='?', default=False, const=True,
                        help='use secure connection')
    args = parser.parse_args()
    return args


def main():
    arguments = get_cli_arguments()
    if not arguments.password:
        print('Exit: password required.')
    else:
        report_devices(arguments)


if __name__ == '__main__':
    main()
