# -*- coding: utf-8 -*-

"""
fritzphonebook.py

Utility module for FritzConnection to access phone books.

License: MIT https://opensource.org/licenses/MIT
Source: https://github.com/kbr/fritzconnection
Author: Klaus Bremer, David M. Straub
"""

import argparse

# tiny hack to run this as a package but also from the command line. In
# the latter case ValueError is raised from python 2.7,
# SystemError from Python 3.5
# ImportError from Python 3.6
try:
    from . import fritzconnection
except (ValueError, SystemError, ImportError):
    import fritzconnection

from lxml import etree

SERVICE = 'X_AVM-DE_OnTel'


# version-access:
def get_version():
    return fritzconnection.get_version()


class FritzPhonebook(object):

    def __init__(self,
                 fc=None,
                 address=fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.FRITZ_USERNAME,
                 password=''):
        super(FritzPhonebook, self).__init__()
        if fc is None:
            fc = fritzconnection.FritzConnection(address, port, user, password)
        self.fc = fc

    def action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def list_phonebooks(self):
        """Get the list of existing phone books as a list of integer IDs."""
        result = self.action('GetPhonebookList')
        try:
            res = result['NewPhonebookList'].split(',')
            res = [int(x) for x in res]
        except KeyError:
            return []
        return res

    def phonebook_info(self, id):
        """Get the URL of the phone book with integer `id`."""
        result = self.action('GetPhonebook', NewPhonebookId=id)
        info = {}
        try:
            info['name'] = result['NewPhonebookName']
            info['url'] = result['NewPhonebookURL']
        except KeyError:
            return {}
        return info

    def get_all_names(self, id):
        """Get a dictionary with all names and their phone numbers for the
        phone book with `id`."""
        url = self.phonebook_info(id)['url']
        pb = etree.parse(url)
        nrs={}
        for contact in pb.getiterator('contact'):
            name = contact.findall('.//realName')
            nr = contact.findall('.//number')
            nrs[name[0].text] = [n.text for n in nr]
        return nrs

    def lookup_names(self, id, number):
        """Look up the names of the contacts with phone number `number`
        in the phone book with `id`."""
        url = self.phonebook_info(id)['url']
        pb = etree.parse(url)
        xpath = ".//contact[telephony/number/text() = '" + number + "']/person/realName"
        names = set()
        for name in pb.xpath(xpath):
            names.add(name.text)
        return list(names)

    def lookup_numbers(self, id, name):
        """Look up the phone numbers of contact `name` in the phone book with
        `id`."""
        url = self.phonebook_info(id)['url']
        pb = etree.parse(url)
        xpath = ".//contact[person/realName/text() = '" + name + "']/telephony/number"
        numbers = set()
        for number in pb.xpath(xpath):
            numbers.add(number.text)
        return list(numbers)

# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def _print_header(fp):
    print('\nFritzPhonebook:')
    print('{:<20}{}'.format('version:', get_version()))
    print('{:<20}{}'.format('model:', fp.modelname))
    print('{:<20}{}'.format('ip:', fp.fc.address))


def print_phonebooks(fp):
    print('\nList of phone books:\n')
    print('{:>3} {:<25} {}\n'.format(
        'ID', 'name', 'url'))
    ids = fp.list_phonebooks
    for i in ids:
        info = fp.phonebook_info(i)
        print('{:>3} {:<25} {}'.format(
            i,
            info['name'],
            info['url'],
            )
        )
    print('\n')


def _print_names(fp, id, number):
    print('\n{}{}:\n'.format('Names for phone number ', number))
    names = fp.lookup_names(id, number)
    for name in names:
        print('{:<23}'.format(name))
    print('\n')


def _print_numbers(fp, id, name):
    print('\n{}{}:\n'.format('Numbers for contact ', name))
    numbers = fp.lookup_numbers(id, name)
    for number in numbers:
        print('{:<23}'.format(number))
    print('\n')


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Phonebook')
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
                        help='List all phone books '
                       '(default if no other options given)')
    parser.add_argument('--phonebook',
                        nargs='?', default=0,
                        help='Phonebook ID for  name or number search')
    parser.add_argument('--name',
                        nargs='?', default=0,
                        help='Name for number search')
    parser.add_argument('--number',
                        nargs='?', default=0,
                        help='Number for name search')
    args = parser.parse_args()
    return args


def _print_status(arguments):
    fp = FritzPhonebook(address=arguments.address,
                    port=arguments.port,
                    user=arguments.username,
                    password=arguments.password)
    _print_header(fp)
    if arguments.number:
        _print_names(fp, arguments.phonebook, arguments.number)
    elif arguments.name:
        _print_numbers(fp, arguments.phonebook, arguments.name)
    else:
        print_phonebooks(fp)


def main():
    _print_status(_get_cli_arguments())


if __name__ == '__main__':
    main()
