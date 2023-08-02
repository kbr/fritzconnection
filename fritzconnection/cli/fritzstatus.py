"""
fritzstatus.py

Module to inspect the FritzBox API for available services and actions.
CLI interface.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..core.exceptions import (
    FritzServiceError,
    FritzActionError,
    FritzAuthorizationError
)
from ..lib.fritzstatus import FritzStatus
from .utils import (
    get_cli_arguments,
    get_instance,
    print_header,
    print_common_exception_message
)


def print_status(fs):
    print("FritzStatus:\n")
    status_information = [
        ("is linked", "is_linked"),
        ("is connected", "is_connected"),
        ("external ip (v4)", "external_ip"),
        ("external ip (v6)", "external_ipv6"),
        ("internal ipv6-prefix", "ipv6_prefix"),
        ("uptime", "str_uptime"),
        ("bytes send", "bytes_sent"),
        ("bytes received", "bytes_received"),
        ("max. bit rate", "str_max_bit_rate"),
    ]
    for status, attribute in status_information:
        try:
            information = getattr(fs, attribute)
        except (FritzServiceError, FritzActionError):
            information = f'unsupported attribute "{attribute}"'
        print(f"    {status:22}: {information}")
    print()


def execute():
    arguments = get_cli_arguments()
    fs = get_instance(FritzStatus, arguments)
    print_header(fs)
    print_status(fs)


def main():
    try:
        execute()
    except FritzAuthorizationError as err:
        # should not happen for this service
        print_common_exception_message(err)


if __name__ == "__main__":
    main()
