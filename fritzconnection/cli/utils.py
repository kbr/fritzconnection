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
    FRITZ_CACHE_FORMAT_PICKLE,
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
    FRITZ_ENV_USERNAME,
    FRITZ_ENV_PASSWORD,
    FRITZ_ENV_USECACHE,
    FRITZ_ENV_CACHEDIRECTORY,
    FRITZ_ENV_CACHE_FORMAT,
)
from ..core.utils import get_bool_env
from .. import __version__


def print_header(instance):
    print(f'\nfritzconnection v{__version__}')
    if isinstance(instance, FritzConnection):
        print(instance)
    else:
        print(instance.fc)
    print()


def print_common_exception_message(error_object):
        print(error_object)
        print(
            "\nSeems you forgot to provide the user and/or the password."
            "\nYou can provide these with the flag -u and -p or store them"
            "\nin the environment as FRITZ_USERNAME and FRITZ_PASSWORD."
            "\n(Environment changes will get recognized by new processes.)\n"
        )


def get_instance(cls, args):
    # -y implies -x:
    if not args.verify_cache:
        args.use_cache = True
    return cls(
        address=args.address,
        port=args.port,
        user=args.username,
        password=args.password,
        use_tls=args.encrypt,
        use_cache=args.use_cache,
        verify_cache=args.verify_cache,
        cache_directory=args.cache_directory,
        cache_format=args.cache_format,
    )


def get_cli_arguments(scan_additional_arguments=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=FRITZ_IP_ADDRESS, const=None,
                        dest='address',
                        help='Specify ip-address of the FritzBox to connect to. '
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
                        help='Flag: use secure connection (TLS)')
    parser.add_argument('-x', '--use-cache',
                        default=get_bool_env(FRITZ_ENV_USECACHE, False),
                        action="store_true",
                        dest='use_cache',
                        help='Flag: use api cache (e[x]cellerate: speed-up subsequent '
                             'instanciations)'
                        )
    parser.add_argument('-y', '--suppress-cache-verification',
                        action='store_false',
                        default=True,
                        dest='verify_cache',  # needs inverted boolean to suppress.
                        help='Flag: suppress cache verification, implies -x'
                        )
    parser.add_argument('--cache-format',
                        nargs='?', default=os.getenv(
                            FRITZ_ENV_CACHE_FORMAT, FRITZ_CACHE_FORMAT_PICKLE
                        ),
                        dest='cache_format',
                        help="cache-file format: json|pickle (default: pickle)"
                        )
    parser.add_argument('--cache-directory',
                        nargs='?',
                        default=os.getenv(FRITZ_ENV_CACHEDIRECTORY, None),
                        const=None,
                        dest='cache_directory',
                        help="path to cache directory (default: ~.fritzconnection)"
                        )
    if scan_additional_arguments:
        scan_additional_arguments(parser)
    args = parser.parse_args()
    return args
