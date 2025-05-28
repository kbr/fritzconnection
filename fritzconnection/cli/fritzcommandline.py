"""
command-line interface for fritzconnection.
"""

import argparse
import textwrap

import fritzconnection
from fritzconnection.core.description import Service

_author_ = "Klaus Bremer"
_version_ = fritzconnection.__version__


PROGRAM_NAME = "fritzconnection"
PROGRAM_DESCRIPTION = textwrap.dedent(f"""\
    command line interface for {PROGRAM_NAME}
    version: {_version_}
""")
SERVICE_HEADER_LINE = "=" * 54


class FritzInspection:

    def __init__(self, args):
        self.args = args  # this is the namespace-object from argparse
        self.fc = fritzconnection.core.fritzconnection.FritzConnection(
            address=args.address,
            port= args.port,
            user=args.username,
            password=args.password,
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
            print("  Error: no actions available\n")


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
        print("  Error: unknown service")
    else:
        print_service(service, with_actions=True, with_args=args.arguments)


def report_complete_api(fi, args):
    """
    Entry point to report the complete api. This can be lengthy, so a
    redirect of stdout to a file could be a good idea.
    """
    print_services(fi, with_actions=True, with_args=True)


def report_hosts(fi, args):
    pass


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
        nargs='?',
        dest='username',
        default=None,
        help='Fritzbox authentication username'
    )
    parser.add_argument(
        '-p', '--password',
        nargs='?',
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
    hosts.set_defaults(func=report_hosts)

    return parser.parse_args()


def main():
    args = get_arguments()

    if hasattr(args, "func"):
        fi = FritzInspection(args)
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
            "  status",
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
