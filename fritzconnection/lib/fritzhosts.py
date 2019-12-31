"""
Modul to list the known hosts. Older versions of FritzOS lists only up
to 16 entries. For newer versions this limitation is gone.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import itertools
from .fritzbase import AbstractLibraryBase


SERVICE = 'Hosts1'


class FritzHosts(AbstractLibraryBase):
    """
    Class to list all known hosts. All parameters are optional. If
    given, they have the following meaning: `fc` is an instance of
    FritzConnection, `address` the ip of the Fritz!Box, `port` the port
    to connect to, `user` the username, `password` the password,
    `timeout` a timeout as floating point number in seconds, `use_tls` a
    boolean indicating to use TLS (default False).
    """

    def _action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    @property
    def host_numbers(self):
        """The number of known hosts."""
        result = self._action('GetHostNumberOfEntries')
        return result['NewHostNumberOfEntries']

    def get_generic_host_entry(self, index):
        """
        Returns a dictionary with informations about a device internally
        registered by the position *index*. Index-positions are
        zero-based.
        """
        result = self._action('GetGenericHostEntry', NewIndex=index)
        return result

    def get_specific_host_entry(self, mac_address):
        """
        Returns a dictionary with informations about a device addressed
        by the MAC-address.
        """
        result = self._action('GetSpecificHostEntry', NewMACAddress=mac_address)
        return result

    def get_hosts_info(self):
        """
        Returns a list of dicts with information about the known hosts.
        The dict-keys are: 'ip', 'name', 'mac', 'status'
        """
        result = []
        for index in itertools.count():
            try:
                host = self.get_generic_host_entry(index)
            except IndexError:
                # no more host entries:
                break
            result.append({
                'ip': host['NewIPAddress'],
                'name': host['NewHostName'],
                'mac': host['NewMACAddress'],
                'status': host['NewActive']})
        return result

