"""
command-line interface for fritzconnection.
"""

import argparse
import textwrap
import types

import fritzconnection
from fritzconnection.core.description import HostItems
from fritzconnection.core.description import Service
from fritzconnection.core.exceptions import FritzConnectionException
from fritzconnection.core.exceptions import FritzServiceError
from fritzconnection.core.utils import get_xml_root
from fritzconnection.lib.fritzwan import FritzStatus

import logging
from fritzconnection.core.logger import activate_local_debug_mode

_author_ = "Klaus Bremer"
_version_ = fritzconnection.__version__


PROGRAM_NAME = "fritzconnection"
PROGRAM_DESCRIPTION = textwrap.dedent(f"""\
    command line interface for {PROGRAM_NAME}
    version: {_version_}
""")
SERVICE_HEADER_LINE = "=" * 54
DEFAULT_TIMEOUT = 3  # the device should respond at least after 3 seconds


class FritzInspection:

    def __init__(self, args):
        self.args = args  # this is the namespace-object from argparse

        # activate_local_debug_mode(handler=logging.FileHandler("debug.txt"))

        self.fc = fritzconnection.core.fritzconnection.FritzConnection(
            address=args.address,
            port= args.port,
            user=args.username,
            password=args.password,
            timeout=DEFAULT_TIMEOUT,
            use_tls=args.encrypt,
            use_cache=not(args.ignore_cache),
            cache_directory=args.cache_directory,
        )

    def get_device_info(self) -> str:
        """
        Returns the device model and system-software version
        """
        return f"{self.fc.device_name}\n{self.fc.system_version}"

    def get_header(self) -> str:
        messages = [
            f"{PROGRAM_NAME} v{_version_}",
            "",
            f"{self.fc.device_name} ({self.fc.ip_address})",
            f"Fritz!OS: {self.fc.system_version}",
            "",
        ]
        return "\n".join(messages)

    def get_upnp_services(self) -> dict:
        return {
            name: value for name, value in
            self.fc.description.upnp_services.items()
            if not name.startswith("any")
        }

    def get_tr64_services(self) -> dict:
        return self.fc.description.tr64_services

    def get_services(self) -> dict:
        return self.fc.description.services

    def get_actions(self, service: Service|str) -> dict:
        """
        Returns the actions of a given service as dict: action-name as
        key, action-object as value.
        """
        if isinstance(service, str):
            service = self.fc.description.services[service]
        return service.actions


def print_service(service, indent=2, with_actions=False, with_args=False):
    postfix = ":\n" if with_actions else ""
    name = f"{' '*indent}{service.short_service_id}{postfix}"
    if postfix:
        print(f"\n{' '*indent}{SERVICE_HEADER_LINE}\n")
    print(name)
    if with_actions:
        argument_textlen = service.get_max_argument_name_len() + 2
        actions = service.actions.values()
        for action in actions:
            print(
                action.get_report(
                    indentation=indent + 2,
                    argument_textlen=argument_textlen,
                    report_arguments=with_args
                )
            )
            if with_args:
                print()
        if not actions:
            print_error_message("no actions available")


def print_services(fi, with_actions=False, with_args=False):
    upnp_services = fi.get_upnp_services().values()
    tr64_services = fi.get_tr64_services().values()
    for name, services in zip(("UPnP", "TR64"), (upnp_services, tr64_services)):
        print(f"\n{' '*2}{name} services:\n")
        if not services:
            print(f"{' '*4}{no_services_message}")
        for service in sorted(services, key=lambda s: s.short_service_id):
            print_service(
                service,
                indent=4,
                with_actions=with_actions,
                with_args=with_args,
            )


def print_error_message(message):
    """use same format for all error-messages"""
    print(f"\n  Error: {message}\n")


def report_services(fi, args):
    """
    Entry point to report all services
    """
    print_services(fi)


def report_service(fi, args):
    """
    Entry point to report the actions of a single service optional with
    the action-arguments
    """
    services = fi.get_services()
    try:
        service = services[args.service_name]
    except KeyError:
        print_error_message("unknown service")
    else:
        print_service(service, with_actions=True, with_args=args.arguments)


def report_complete_api(fi, args):
    """
    Entry point to report the complete api. This can be lengthy, so a
    redirect of stdout to a file could be a good idea.
    """
    print_services(fi, with_actions=True, with_args=True)


def report_hosts(fi, args):
#     activate_local_debug_mode(handler=logging.FileHandler("debug.txt"))
    result = fi.fc.call_action("Hosts1", "X_AVM-DE_GetHostListPath")
    path = result["NewX_AVM-DE_HostListPath"]
    url = fi.fc.address + path
    root = get_xml_root(source=url, session=fi.fc.session)
    hosts = HostItems()
    hosts.load(root)

    if args.active:
        hosts = [host for host in hosts if host.Active == "1"]
    max_hostname_len = 0
    for host in hosts:
        if host.IPAddress is None:
            host.IPAddress = "-"
        max_hostname_len = max(len(host.HostName), max_hostname_len)
    max_hostname_len += 2
    h_ip = "ip-address"
    h_hn = "hostname"
    header = f"\n     {h_ip:18}{h_hn:{max_hostname_len-4}}active\n"
    print(header)
    for i, host in enumerate(hosts, start=1):
        line = f"{i:>2d}   {host.IPAddress:18}{host.HostName:{max_hostname_len}}"\
               f"{host.Active:>2}"
        print(line)


def report_status(fi, args):
    """
    Report the WAN status of a device
    """
    try:
        fs = FritzStatus(fi.fc)
    except FritzServiceError:
        # call to 'Layer3Forwarding1' fails on non-WAN devices:
        print_error_message("the device is not a WAN-device")
    else:
        result = fs.get_status_information()
        max_key_len = len(max(result.keys(), key=len))
        for key, value in result.items():
            print(f"  {key:{max_key_len + 1}}:  {value}")


def get_common_arguments(parser):
    parser.add_argument(
        '-i', '--ip-address',
        nargs='?',
        dest='address',
        default=None,
        help='Specify ip-address of the Device to connect to. '
    )
    parser.add_argument(
        '--port',
        nargs='?',
        dest='port',
        default=None,
        help='Port of the Device to connect to. '
    )
    parser.add_argument(
        '-u', '--username',
        dest='username',
        default=None,
        help='Fritzbox authentication username'
    )
    parser.add_argument(
        '-p', '--password',
        dest='password',
        default=None,
        help='Fritzbox authentication password'
    )
    parser.add_argument(
        '-e', '--encrypt',
        dest='encrypt',
        action="store_true",
        help='Flag: use secure connection (TLS)'
    )
    parser.add_argument(
        '--ignore-cache',
        dest='ignore_cache',
        action="store_true",
        help='Ignore existing cache and load data from device'
    )
    parser.add_argument(
        '--cache-directory',
        nargs='?',
        dest='cache_directory',
        default=None,
        help="path to cache directory (default: ~.fritzconnection)"
    )


def get_arguments():
    parser = argparse.ArgumentParser(
        prog=PROGRAM_NAME,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=PROGRAM_DESCRIPTION,
    )
    subparsers = parser.add_subparsers(help="Available subcommands")

    services = subparsers.add_parser("services")
    get_common_arguments(services)
    services.set_defaults(func=report_services)

    actions = subparsers.add_parser("service")
    get_common_arguments(actions)
    actions.add_argument(
        '-s', '--service-name',
        dest='service_name',
        required=True,
        help='Servicename to list actions'
    )
    actions.add_argument(
        '-a', '--arguments',
        dest='arguments',
        action='store_true',
        help='list arguments for actions.'
    )
    actions.set_defaults(func=report_service)

    complete = subparsers.add_parser("complete")
    get_common_arguments(complete)
    complete.set_defaults(func=report_complete_api)

    hosts = subparsers.add_parser("hosts")
    get_common_arguments(hosts)
    hosts.add_argument(
        '-a', '--active',
        dest='active',
        action='store_true',
        help='list only active hosts.'
    )
    hosts.set_defaults(func=report_hosts)

    status = subparsers.add_parser("status")
    get_common_arguments(status)
    status.set_defaults(func=report_status)

    return parser.parse_args()


def main():
    args = get_arguments()

    if hasattr(args, "func"):
        try:
            fi = FritzInspection(args)
        except FritzConnectionException:
            print_error_message("unable to connect to the device")
        else:
            header = fi.get_header()
            print(header)
            args.func(fi, args)
            print()
    else:
        msg = (
            "",
            "Please specify a subcommand to run.",
            "Available subcommands are:",
            "",
            "  status       list information about the current wan status",
            "  service      list actions and arguments for a single service",
            "  services     list all available services",
            "  hosts        list the connected hosts",
            "  complete     list the complete API (output could be huge)",
            "",
            "use -h for help",
            "",
        )
        print("\n".join(msg))


if __name__ == "__main__":
    main()
