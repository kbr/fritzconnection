"""
fritzphonebook.py

Module to inspect the Fritz!Box phonebooks.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Authors: Klaus Bremer, David M. Straub
"""

from ..core.exceptions import FritzAuthorizationError
from ..lib.fritzphonebook import FritzPhonebook
from .utils import (
    get_cli_arguments,
    get_instance,
    print_header,
    print_common_exception_message
)


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


def add_arguments(parser):
    parser.add_argument('-a', '--all',
                        action='store_true',
                        help='List all phone books ')
    parser.add_argument('--name',
                        nargs='?', default=0,
                        help='Name for number search')
    parser.add_argument('--number',
                        nargs='?', default=0,
                        help='Number for name search')


def execute():
    arguments = get_cli_arguments(add_arguments)
    fpb = get_instance(FritzPhonebook, arguments)
    print_header(fpb)
    print('FritzPhonebook:\n')
    if arguments.all:
        print_phonebooks(fpb)
    elif arguments.name:
        print_search_name(fpb, arguments)
    elif arguments.number:
        print_search_number(fpb, arguments)
    print()  # blank line for better readability


def main():
    try:
        execute()
    except FritzAuthorizationError as err:
        # should not happen for this service
        print_common_exception_message(err)


if __name__ == '__main__':
    main()
