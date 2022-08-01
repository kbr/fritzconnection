"""
utils.py

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

import argparse
import os

from ..core.fritzconnection import (
    FritzConnection,
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
    FRITZ_ENV_USERNAME,
    FRITZ_ENV_PASSWORD,
    FRITZ_ENV_USECACHE,
    FRITZ_ENV_CACHEDIRECTORY,
)
from .. import __version__


def print_header(instance):
    print(f'\nfritzconnection v{__version__}')
    if isinstance(instance, FritzConnection):
        print(instance)
    else:
        print(instance.fc)
    print()


def get_instance(cls, args):
    return cls(
        address=args.address,
        port=args.port,
        user=args.username,
        password=args.password,
        use_tls=args.encrypt,
        use_cache=args.use_cache,
        cache_directory=args.cache_directory,
    )


def get_cli_arguments(scan_additional_arguments=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=FRITZ_IP_ADDRESS, const=None,
                        dest='address',
                        help='Specify ip-address of the FritzBox to connect to.'
                             'Default: %s' % FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        help='Port of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs='?', default=os.getenv(FRITZ_ENV_USERNAME, None),
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=os.getenv(FRITZ_ENV_PASSWORD, None),
                        help='Fritzbox authentication password')
    parser.add_argument('-e', '--encrypt',
                        nargs='?', default=False, const=True,
                        help='Flag: use secure connection')
    parser.add_argument('-C', '--use-cache',
                        nargs='?', default=os.getenv(FRITZ_ENV_USECACHE, None),
                        dest='use_cache',
                        help='Flag: use api cache (speed-up subsequent '
                             'instanciations)')
    parser.add_argument('--cache-directory',
                        nargs='?',
                        default=os.getenv(FRITZ_ENV_CACHEDIRECTORY, None),
                        const=None,
                        dest='cache_directory',
                        help="path to cache directory if it's not the "
                             "default one")

    if scan_additional_arguments:
        scan_additional_arguments(parser)
    args = parser.parse_args()
    return args
