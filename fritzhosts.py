# -*- coding: utf-8 -*-

_version_ = '0.1.0'

import argparse
import fritzconnection


SERVICE = 'Hosts'


# version-access:
def get_version():
    return _version_


class FritzHosts(object):

    def __init__(self,
                 fc=None,
                 address=fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.FRITZ_USERNAME,
                 password=''):
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


# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def _print_header(fh):
    print('\nFritzHosts:')
    print('{:<20}{}'.format('version:', get_version()))
    print('{:<20}{}'.format('model:', fh.modelname))
    print('{:<20}{}'.format('ip:', fh.fc.address))


def _print_hosts(fh):
    print('\nList of registered hosts:\n')
    print('{:>3}: {:<15} {:<26} {:<17}   {}\n'.format(
        'n', 'ip', 'name', 'mac', 'status'))
    index = 0
    host_num = fh.host_numbers
    while index < host_num:
        host = fh.get_generic_host_entry(index)
        if host['NewActive'] == '1':
            status = 'active'
        else:
            status = '-'
        print('{:>3}: {:<15} {:<26} {:<17}   {}'.format(
            index,
            host['NewIPAddress'],
            host['NewHostName'],
            host['NewMACAddress'],
            status,
            )
        )
        index += 1
    print('\n')


def _print_detail(fh, detail):
    mac_address = detail[0]
    print('\n{:<23}{}\n'.format('Details for host:', mac_address))
    info = fh.get_specific_host_entry(mac_address)
    for key, value in info.items():
        print('{:<23}: {}'.format(key, value))
    print('\n')


def _print_nums(fh):
    print('{:<20}{}\n'.format('Number of hosts:', fh.host_numbers))


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Hosts')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=fritzconnection.FRITZ_IP_ADDRESS,
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=fritzconnection.FRITZ_TCP_PORT,
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs=1, default=fritzconnection.FRITZ_USERNAME,
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs=1, default='',
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
    args = parser.parse_args()
    return args


def _print_status(arguments):
    fh = FritzHosts(address=arguments.address,
                    port=arguments.port,
                    user=arguments.username,
                    password=arguments.password)
    _print_header(fh)
    if arguments.detail:
        _print_detail(fh, arguments.detail)
    elif arguments.nums:
        _print_nums(fh)
    else:
        _print_hosts(fh)


if __name__ == '__main__':
    _print_status(_get_cli_arguments())
