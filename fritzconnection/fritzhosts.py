# -*- coding: utf-8 -*-

"""
fritzhosts.py

Utility modul for FritzConnection to list the known hosts.

Older versions of FritzOS lists only up to 16 entries.
For newer versions this limitation is gone.

License: MIT https://opensource.org/licenses/MIT
Source: https://github.com/kbr/fritzconnection
Author: Klaus Bremer
"""

import os, argparse

# tiny hack to run this as a package but also from the command line. In
# the latter case ValueError is raised from python 2.7,
# SystemError from Python 3.5
# ImportError from Python 3.6
try:
    from . import fritzconnection
except (ValueError, SystemError, ImportError):
    import fritzconnection


SERVICE = 'Hosts'


# version-access:
def get_version():
    return fritzconnection.get_version()


class FritzHosts(object):

    def __init__(self, fc=None, address=None, port=None, user=None, password=None):
        super(FritzHosts, self).__init__()
        if fc is None:
            fc = fritzconnection.FritzConnection(address, port, user, password)
        self.fc = fc

    def action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def host_numbers(self):
        result = self.action('GetHostNumberOfEntries')
        return result['NewHostNumberOfEntries']

    def get_generic_host_entry(self, index):
        result = self.action('GetGenericHostEntry', NewIndex=index)
        return result

    def get_specific_host_entry(self, mac_address):
        result = self.action('GetSpecificHostEntry', NewMACAddress=mac_address)
        return result

    def get_hosts_info(self):
        """
        Returns a list of dicts with information about the known hosts.
        The dict-keys are: 'ip', 'name', 'mac', 'status'
        """
        result = []
        for index in range(self.host_numbers):
            host = self.get_generic_host_entry(index)
            result.append({
                'ip': host['NewIPAddress'],
                'name': host['NewHostName'],
                'mac': host['NewMACAddress'],
                'status': host['NewActive']})
        return result


# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def _print_header(fh):
    print('\nFritzHosts:')
    print('{:<20}{}'.format('version:', get_version()))
    print('{:<20}{}'.format('model:', fh.modelname))
    print('{:<20}{}'.format('ip:', fh.fc.address))


def print_hosts(fh):
    print('\nList of registered hosts:\n')
    print('{:>3}: {:<15} {:<26} {:<17}   {}\n'.format(
        'n', 'ip', 'name', 'mac', 'status'))
    hosts = fh.get_hosts_info()
    for index, host in enumerate(hosts):
        status = 'active' if host['status'] == '1' else  '-'
        ip = '-' if host['ip'] == None else host['ip']
        mac = '-' if host['mac'] == None else host['mac']
        print('{:>3}: {:<15} {:<26} {:<17}   {}'.format(
            index,
            ip,
            host['name'],
            mac,
            status,
            )
        )
    print('\n')


def _print_detail(fh, detail, quiet):
    mac_address = detail[0].upper()
    info = fh.get_specific_host_entry(mac_address)
    if info:
        if not quiet:
            print('\n{:<23}{}\n'.format('Details for host:', mac_address))
            for key, value in info.items():
                print('{:<23}: {}'.format(key, value))
            print('\n')
        else:
            print(info['NewActive'])
    else:
        print('0')

def _print_nums(fh):
    print('{:<20}{}\n'.format('Number of hosts:', fh.host_numbers))


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Hosts')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=None, const=None,
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=None, const=None,
                        help='Fritzbox authentication password')
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
    parser.add_argument('-q', '--quiet',
                        action='store_true',
                        help='Quiet mode '
                             '(just return state as 0|1 for requested mac address)')
    args = parser.parse_args()
    return args


def _print_status(arguments):
    fh = FritzHosts(address=arguments.address,
                    port=arguments.port,
                    user=arguments.username,
                    password=arguments.password)
    if not arguments.quiet:
        _print_header(fh)
    if arguments.detail:
        _print_detail(fh, arguments.detail, arguments.quiet)
    elif arguments.nums:
        _print_nums(fh)
    else:
        print_hosts(fh)

def main():
    _print_status(_get_cli_arguments())

if __name__ == '__main__':
    main()
