"""
fritzhosts.py

Utility modul for FritzConnection to list the known hosts.

Older versions of FritzOS lists only up to 16 entries.
For newer versions this limitation is gone.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT (https://opensource.org/licenses/MIT)
Author: Klaus Bremer
"""

from ..core import FritzConnection


SERVICE = 'Hosts'


class FritzHosts:
    """Class to list all known hosts.
    """

    def __init__(self, fc=None, address=None, port=None, user=None, password=None):
        super().__init__()
        if fc is None:
            fc = FritzConnection(address, port, user, password)
        self.fc = fc

    def action(self, actionname, **kwargs):
        return self.fc.call_action(SERVICE, actionname, **kwargs)

    @property
    def modelname(self):
        return self.fc.modelname

    @property
    def host_numbers(self):
        result = self.action('GetHostNumberOfEntries')
        return result['NewHostNumberOfEntries']

    def get_generic_host_entry(self, index):
        result = self.action('GetGenericHostEntry', NewIndex=index)
        return result

    def get_specific_host_entry(self, mac_address):
        result = self.action('GetSpecificHostEntry', NewMACAddress=mac_address)
        return result

    def get_hosts_info(self):
        """
        Returns a list of dicts with information about the known hosts.
        The dict-keys are: 'ip', 'name', 'mac', 'status'
        """
        result = []
        for index in range(self.host_numbers):
            host = self.get_generic_host_entry(index)
            result.append({
                'ip': host['NewIPAddress'],
                'name': host['NewHostName'],
                'mac': host['NewMACAddress'],
                'status': host['NewActive']})
        return result

