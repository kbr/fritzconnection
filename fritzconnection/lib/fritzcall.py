"""
FritzCall:

Gives access to recent phone calls: incoming, outgoing and
missed ones.

Utility module based on FritzConnection.
Author: Klaus Bremer
"""


import argparse
import os

# tiny hack to run this as a package but also from the command line. In
# the latter case ValueError is raised from python 2.7,
# SystemError from Python 3.5
# ImportError from Python 3.6
try:
    from . import fritzconnection
except (ValueError, SystemError, ImportError):
    import fritzconnection

from datetime import datetime, timedelta
from lxml import etree


# calltypes
ALL_CALL_TYPES = 0
RECEIVED_CALL_TYPE = 1
MISSED_CALL_TYPE = 2
OUT_CALL_TYPE = 3

CALL_TYPES = {
    RECEIVED_CALL_TYPE: 'in',
    MISSED_CALL_TYPE: 'missed',
    OUT_CALL_TYPE: 'out',
}

# access requires password
ONTEL_SERVICE = 'X_AVM-DE_OnTel'

# version-access:
def get_version():
    return fritzconnection.get_version()


class FritzCall(object):
    """
    Gives access to lists of recent phone calls: incoming, outgoing and
    missed ones.
    """

    def __init__(self,
                 fc=None,
                 address=fritzconnection.FRITZ_IP_ADDRESS,
                 port=fritzconnection.FRITZ_TCP_PORT,
                 user=fritzconnection.FRITZ_USERNAME,
                 password=''):
        super(FritzCall, self).__init__()
        if fc is None:
            fc = fritzconnection.FritzConnection(address, port, user, password)
        self.fc = fc
        self.calls = None

    def _get_calllist_iterator(self):
        result = self.fc.call_action(ONTEL_SERVICE, 'GetCallList')
        url = result['NewCallListURL']
        return etree.parse(url).getiterator()

    def _update(self, update=True):

        def get_duration(value):
            h, m = map(int, value.strip().split(':'))
            return timedelta(minutes=m, hours=h)

        def converter(entry):
            for k, v in (('Type', int), ('Id', int), ('Port', int)):
                entry[k] = v(entry[k])
            entry['Date'] = datetime.strptime(entry['Date'], '%d.%m.%y %H:%M')
            entry['Duration'] = get_duration(entry['Duration'])
            return entry

        if not self.calls:
            update = True
        if update:
            root = self._get_calllist_iterator()
            # convert elements with content to a list of dicts
            nodes = [
                {node.tag: node.text for node in elem}
                for elem in root if len(elem)
            ]
            # convert value-types for valid nodes
            self.calls = map(converter,
                [node for node in nodes if node.get('Id')])

    # ----------------------------------
    # public api:
    # ----------------------------------

    def get_calls(self, calltype=ALL_CALL_TYPES, update=True):
        """
        Returns a list of dicts. Every dictionary represents a call.
        Keys and types are:

        Id: int
        Type: int
        Caller: str
        Called: str
        CalledNumber: str
        Name: str
        Numbertype: str
        Device: str
        Port: int
        Date: datetime
        Duration: timedelta
        Count: str
        Path: str

        The values are either of the given type or None.
        """
        self._update(update)
        if calltype == ALL_CALL_TYPES:
            return self.calls
        return [call for call in self.calls if call.get('Type')==calltype]

    def get_received_calls(self, update=True):
        """Returns a list of dicts of calls from Type 1 (in)"""
        return self.get_calls(RECEIVED_CALL_TYPE, update)

    def get_missed_calls(self, update=True):
        """Returns a list of dicts of calls from Type 2 (missed)"""
        return self.get_calls(MISSED_CALL_TYPE, update)

    def get_out_calls(self, update=True):
        """Returns a list of dicts of calls from Type 3 (out)"""
        return self.get_calls(OUT_CALL_TYPE, update)


# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def print_calls(fc, calltype, num):
    print(calltype)
    template = '{:<7}{:<16}{:<16}{:<20}{}'
    calls = list(fc.get_calls(calltype))
    stored_numbers = len(calls)
    print('Numbers in storage:', stored_numbers)
    print('Entries listed:', min(num, stored_numbers))
    print(template.format('Type', 'from', 'to', 'date/time', 'duration'))
    for n, call in enumerate(calls):
        if n >= num:
            break
        calltype = CALL_TYPES.get(call.get('Type'), '-')
        caller = call.get('Caller')
        caller = caller.split()[-1] if caller else '-'
        called = call.get('Called')
        called = called.split()[-1] if called else '-'
        date = call.get('Date')
        if date:
            date = date.strftime('%Y-%m-%d %H:%M')
        duration = call.get('Duration')
        print(template.format(calltype, caller, called, date, duration))


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------


def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Hosts')
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
                        help='Show all calls '
                             '(default if no other options given)')
    parser.add_argument('-r', '--received',
                        action='store_true',
                        help='Show received (incoming) calls')
    parser.add_argument('-o', '--out',
                        action='store_true',
                        help='Show outgoing calls')
    parser.add_argument('-m', '--missed',
                        action='store_true',
                        help='Show missed calls')
    parser.add_argument('-n', '--num', type=int,
                        nargs='?', default=999, const=999,
                        help='max number of calls')
    args = parser.parse_args()
    return args


def _print_status(arguments):
    fc = FritzCall(address=arguments.address,
                   port=arguments.port,
                   user=arguments.username,
                   password=arguments.password)
    if arguments.received:
        calltype = RECEIVED_CALL_TYPE
    elif arguments.missed:
        calltype = MISSED_CALL_TYPE
    elif arguments.out:
        calltype = OUT_CALL_TYPE
    else:
        calltype = ALL_CALL_TYPES
    print_calls(fc, calltype, arguments.num)


def main():
    _print_status(_get_cli_arguments())


if __name__ == '__main__':
    main()
