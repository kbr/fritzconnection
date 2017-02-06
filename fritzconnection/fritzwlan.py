# -*- coding: utf-8 -*-

"""
fritzwlan.py

Utility modul for FritzConnection to list the known WLAN connections.
Based on fritzhosts from Klaus Bremer https://bitbucket.org/kbr/fritzconnection
License: MIT https://opensource.org/licenses/MIT
Author: Bernd Strebel
"""

import os, argparse

# tiny hack to run this as a package but also from the command line. In
# the latter case ValueError is raised from python 2.7 and SystemError
# from Python 3.5
try:
    from . import fritzconnection
except (ValueError, SystemError):
    import fritzconnection

__version__ = '0.5.1'

SERVICE = 'WLANConfiguration'

# version-access:
def get_version():
    return __version__

class FritzWLAN(object):

    def __init__(self,
                 fc=None,
                 address=fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.FRITZ_USERNAME,
                 password=''):
        super(FritzWLAN, self).__init__()
        if fc is None:
            fc = fritzconnection.FritzConnection(address, port, user, password)
        self.fc = fc
        self.service = 0

    def action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE+':'+self.service, actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def host_numbers(self):
        result = self.action('GetTotalAssociations')
        return result['NewTotalAssociations']

    def get_generic_host_entry(self, index):
        result = self.action('GetGenericAssociatedDeviceInfo', NewAssociatedDeviceIndex=index)
        return result

    def get_specific_host_entry(self, mac_address):
        result = self.action('GetSpecificAssociatedDeviceInfo', NewAssociatedDeviceMACAddress=mac_address)
        return result

    def get_hosts_info(self):
        """
        Returns a list of dicts with information about the known hosts.
        The dict-keys are: 'auth', 'mac', 'ip', 'signal', 'speed'
        """
        result = []
        index = 0
        while index < self.host_numbers:
            host = self.get_generic_host_entry(index)
            if host:
                result.append({
                    'service': self.service,
                    'index': index,
                    'status': host['NewAssociatedDeviceAuthState'],
                    'mac': host['NewAssociatedDeviceMACAddress'],
                    'ip': host['NewAssociatedDeviceIPAddress'],
                    'signal': host['NewX_AVM-DE_SignalStrength'],
                    'speed': host['NewX_AVM-DE_Speed']
                })
            index += 1
        return result


# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def _print_header(fh):
    print('\nFritzHosts:')
    print('{:<30}{}'.format('version:', get_version()))
    print('{:<30}{}'.format('model:', fh.modelname))
    print('{:<30}{}'.format('ip:', fh.fc.address))

def print_hosts(fh):
    print('\n{}\n'.format(SERVICE+':'+ fh.service))
    print('{:>5} {:<7} {:<15} {:<17} {:<7} {:>7} {:>7}\n'.format(
        'index', 'status', 'ip', 'mac', 'service', 'signal', 'speed'))
    hosts = fh.get_hosts_info()
    for index, host in enumerate(hosts):
        status = 'active' if host['status'] == '1' else  '-'
        ip = '-' if host['ip'] == None else host['ip']
        mac = '-' if host['mac'] == None else host['mac']
        print('{:>4}: {:<7} {:<15} {:<17} {:<7} {:>7} {:>7}'.format(
            host['index'],
            status,
            ip,
            mac,
            host['service'],
            host['signal'],
            host['speed'],
            )
        )

def _print_detail(fh, detail):
    mac_address = detail[0].lower()
    info = fh.get_specific_host_entry(mac_address)
    if info:
        print('\n{:<30}{}'.format('Details for host:', mac_address))
        print('{:<30}{}\n'.format('', SERVICE+':'+fh.service, fh.host_numbers))
        for key, value in info.items():
            print('{:<30}: {}'.format(key, value))
    # print('\n')


def _print_nums(fh):
    print('{}: {}'.format(SERVICE+':'+fh.service, fh.host_numbers))

# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox WLAN')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=os.getenv('FRITZ_IP_ADDRESS', fritzconnection.FRITZ_IP_ADDRESS),
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=os.getenv('FRITZ_TCP_PORT', fritzconnection.FRITZ_TCP_PORT),
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs=1, default=os.getenv('FRITZ_USERNAME', fritzconnection.FRITZ_USERNAME),
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs=1, default=os.getenv('FRITZ_PASSWORD',''),
                        help='Fritzbox authentication password')
    parser.add_argument('-s', '--service',
                        nargs=1, default='1,2,3',
                        help='WLANConfiguration service number(s)')
    parser.add_argument('-a', '--all',
                        action='store_true',
                        help='Show all hosts '
                             '(default if no other options given)')
    parser.add_argument('-n', '--nums',
                        action='store_true',
                        help='Show number of known hosts')
    parser.add_argument('-d', '--detail',
                        nargs=1, default='',
                        help='Show information about a specific host '
                             '(DETAIL: MAC Address)')
    args = parser.parse_args()
    return args


def _print_status(arguments):
    fh = FritzWLAN(address=arguments.address,
                   port=arguments.port,
                   user=arguments.username,
                   password=arguments.password)

    _print_header(fh)
    # print('')

    services = arguments.service[0] if type(arguments.service) is list else arguments.service

    for service in services.split(','):
        fh.service = service
        if arguments.detail:
            _print_detail(fh, arguments.detail)
        elif arguments.nums:
            _print_nums(fh)
        else:
            print_hosts(fh)


if __name__ == '__main__':
    _print_status(_get_cli_arguments())
