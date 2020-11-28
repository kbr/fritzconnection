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
        help="Setting for internal health-check timeout [sec]."
        "Default: %s" % HEALTHCHECK_TIMEOUT,
    )
    args = parser.parse_args()
    return args


def read_events(fm, event_queue, healthcheck_timeout):
    """
    Report events to stdout in real time.
    Runs until connection to the router fails or terminated by keyboard-interrupt.
    """
    while True:
        try:
            event = event_queue.get(timeout=healthcheck_timeout)
        except queue.Empty:
            # check health:
            if not fm.is_alive:
                print("Error: fritzmonitor connection failed")
                break
        else:
            print(event)


def start_read_events(fm, event_queue, healthcheck_timeout):
    """
    Runs until connection to the router fails or terminted by keyboard-interrupt.
    """
    try:
        read_events(fm, event_queue, healthcheck_timeout)
    except KeyboardInterrupt:
        fm.stop()
    print("\nexit fritzmonitor.\n")


def main():
    """
    Entry point: example to use FritzMonitor.
    """
    args = get_cli_arguments()
    print_header(args)
    # create a FritzMonitor instance and get the event_queue by calling start().
    # start() returns the queue for the events.
    fm = FritzMonitor(address=args.address, timeout=args.timeout)
    try:
        event_queue = fm.start()
    except OSError as err:
        # unable to start:
        print(err)
    else:
        # on success read events from the queue:
        print(
            "start listening for events "
            "(to stop press ^C, for stopping reaction time may be up to socket-timeout):\n"
        )
        start_read_events(fm, event_queue, healthcheck_timeout=args.healthcheck)


if __name__ == "__main__":
    main()
