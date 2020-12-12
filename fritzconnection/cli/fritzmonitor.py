""""
Module to inspect phone-call events in real time.

This is the command line interface for the core.fritzmonitor module
and should serve as an example how to use an instance of FritzMonitor.

To run this, the CallMonitor service of the box has to be activated.
This can be done with any registered Phone by typing the following codes:
activate: #96*5*
deactivate: #96*4* 
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import argparse
import queue

from ..core.fritzmonitor import (
    FritzMonitor,
    FRITZ_IP_ADDRESS,
    FRITZ_MONITOR_SOCKET_TIMEOUT,
)
from .. import __version__


HEALTHCHECK_TIMEOUT = 10


def print_header(args):
    print(f"\nfritzconnection v{__version__}")
    print(f"start fritzmonitor on address: {args.address}")
    print(f"settings for socket-timeout: {args.timeout} [sec]")
    print(f"settings for healthcheck-timeout: {args.healthcheck} [sec]")
    print("(to stop press ^C)\n")


def get_cli_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--ip-address",
        nargs="?",
        default=FRITZ_IP_ADDRESS,
        const=None,
        dest="address",
        help="Specify ip-address of the FritzBox to connect to."
        "Default: %s" % FRITZ_IP_ADDRESS,
    )
    parser.add_argument(
        "-t",
        "--timeout",
        nargs="?",
        type=int,
        default=FRITZ_MONITOR_SOCKET_TIMEOUT,
        const=None,
        dest="timeout",
        help="Setting for socket timeout [sec]."
        "Default: %s" % FRITZ_MONITOR_SOCKET_TIMEOUT,
    )
    parser.add_argument(
        "-c",
        "--healthcheck",
        nargs="?",
        type=int,
        default=HEALTHCHECK_TIMEOUT,
        const=None,
        dest="healthcheck",
        help="Setting for internal health-check interval [sec]."
        "Default: %s" % HEALTHCHECK_TIMEOUT,
    )
    args = parser.parse_args()
    return args


def process_events(monitor, event_queue, healthcheck_interval):
    while True:
        try:
            event = event_queue.get(timeout=healthcheck_interval)
        except queue.Empty:
            # check health:
            if not monitor.is_alive:
                raise OSError("Error: fritzmonitor connection failed")
        else:
            # do event processing here:
            print(event)


def main():
    """
    Entry point: example to use FritzMonitor.
    """
    args = get_cli_arguments()
    print_header(args)
    # create a FritzMonitor instance and get the event_queue by calling start().
    # start() returns the queue for the events.
    try:
        with FritzMonitor(address=args.address, timeout=args.timeout) as monitor:
            event_queue = monitor.start()
            process_events(monitor, event_queue, healthcheck_interval=args.healthcheck)
    except (OSError, KeyboardInterrupt) as err:
        print(err)
    print("exit fritzmonitor")


if __name__ == "__main__":
    main()
