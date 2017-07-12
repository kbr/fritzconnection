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

__version__ = '0.6.5'

ALL_CALL_TYPES = 0
RECEIVED_CALL_TYPE = 1
MISSED_CALL_TYPE = 2
OUT_CALL_TYPE = 3

# access requires password
ONTEL_SERVICE = 'X_AVM-DE_OnTel'

# version-access:
def get_version():
    return __version__


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
    calls = fc.get_calls(calltype)
    for call in calls:
        print(call)


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------


def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox Hosts')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=os.getenv('FRITZ_IP_ADDRESS', fritzconnection.FRITZ_IP_ADDRESS),
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=os.getenv('FRITZ_TCP_PORT', fritzconnection.FRITZ_TCP_PORT),
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % fritzconnection.FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs=1, default=os.getenv('FRITZ_USERNAME', fritzconnection.FRITZ_USERNAME),
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs=1, default=os.getenv('FRITZ_PASSWORD',''),
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
    parser.add_argument('-n', '--num',
                        nargs=1, default=999,
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
