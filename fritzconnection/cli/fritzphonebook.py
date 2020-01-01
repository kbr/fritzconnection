"""
fritzphonebook.py

Module to inspect the Fritz!Box phonebooks.
CLI interface.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Authors: Klaus Bremer, David M. Straub


import argparse

from .. import package_version
from ..lib.fritzphonebook import FritzPhonebook
from ..core.fritzconnection import (
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
)


def print_header(fpb):
    print(f'\nFritzConnection v{package_version}')
    print(f'FritzPhonebook for {fpb.fc}\n')


def print_phonebooks(fpb):
    for id in fpb.phonebook_ids:
        info = fpb.phonebook_info(id)
        print(f"Content of phonebook: {info['name']} ")
        for name, numbers in fpb.get_all_names(id).items():
            print(f"{name:<30}{', '.join(numbers)}")
        print()


def print_search_name(fpb, arguments):
    found = False
    for id in fpb.phonebook_ids:
        contacts = fpb.get_all_names(id)
        numbers = contacts.get(arguments.name)
        if numbers:
            print(f"{arguments.name:<30}{', '.join(numbers)}")
            found = True
    if not found:
        print(f"name {arguments.name} not found.")


def print_search_number(fpb, arguments):
    found = False
    for id in fpb.phonebook_ids:
        numbers = fpb.get_all_numbers(id)
        if arguments.number in numbers:
            print(f"{numbers[arguments.number]:<30}{arguments.number}")
            found = True
    if not found:
        print(f'number {arguments.number} not found.')


def get_cli_arguments():
    parser = argparse.ArgumentParser(description='Fritz!Box Phonebook')
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
    parser.add_argument('-a', '--all',
                        action='store_true',
                        help='List all phone books ')
    parser.add_argument('--name',
                        nargs='?', default=0,
                        help='Name for number search')
    parser.add_argument('--number',
                        nargs='?', default=0,
                        help='Number for name search')
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
    fpb = FritzPhonebook(address=arguments.address,
                         port=arguments.port,
                         user=arguments.username,
                         password=arguments.password,
                         use_tls=arguments.encrypt)
    print_header(fpb)
    if arguments.all:
        print_phonebooks(fpb)
    elif arguments.name:
        print_search_name(fpb, arguments)
    elif arguments.number:
        print_search_number(fpb, arguments)
    print()  # blank line for better readability


if __name__ == '__main__':
    main()
