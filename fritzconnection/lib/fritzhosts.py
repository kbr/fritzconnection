"""
Modul to access and control the known hosts.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import itertools
from ..core.exceptions import (
    FritzArgumentError,
    FritzLookUpError,
)
from .fritzbase import AbstractLibraryBase


SERVICE = 'Hosts1'


class FritzHosts(AbstractLibraryBase):
    """
    Class to access the registered hosts. All parameters are optional. If
    given, they have the following meaning: `fc` is an instance of
    FritzConnection, `address` the ip of the Fritz!Box, `port` the port
    to connect to, `user` the username, `password` the password,
    `timeout` a timeout as floating point number in seconds, `use_tls` a
    boolean indicating to use TLS (default False).
    """

    def _action(self, actionname, *, arguments=None, **kwargs):
        return self.fc.call_action(
            SERVICE, actionname, arguments=arguments, **kwargs
        )

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
        return self._action('GetGenericHostEntry', NewIndex=index)

    def get_specific_host_entry(self, mac_address):
        """
        Returns a dictionary with informations about a device addressed
        by the MAC-address.
        """
        return self._action('GetSpecificHostEntry', NewMACAddress=mac_address)

    def get_specific_host_entry_by_ip(self, ip):
        """
        Returns a dictionary with informations about a device addressed
        by the ip-address. Provides additional information about
        connection speed and system-updates for AVM devices.
        """
        return self._action('X_AVM-DE_GetSpecificHostEntryByIP',NewIPAddress=ip)

    def get_host_status(self, mac_address):
        """
        Provides status information about the device with the given
        `mac_address`. Returns `True` if the device is active or `False`
        otherwise. Returns `None` if the device is not known or the
        `mac_address` is invalid.
        """
        try:
            result = self.get_specific_host_entry(mac_address)
        except (FritzArgumentError, FritzLookUpError):
            return None
        return result['NewActive']

    def get_active_hosts(self):
        """
        Returns a list of dicts with information about the active
        devices. The dict-keys are: 'ip', 'name', 'mac', 'status'
        """
        return [host for host in self.get_hosts_info() if host['status']]

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

    def get_mesh_topology(self, raw=False):
        """
        Returns information about the mesh network topology. If `raw` is
        `False` the topology gets returned as a dictionary with a list
        of nodes. If `raw` is `True` the data are returned as text in
        json format. Default is `False`.
        """
        result = self._action('X_AVM-DE_GetMeshListPath')
        path = result['NewX_AVM-DE_MeshListPath']
        url = f'{self.fc.address}:{self.fc.port}{path}'
        with self.fc.session.get(url) as response:
            return response.text if raw else response.json()

    def get_wakeonlan_status(self, mac_address):
        """
        Returns a boolean whether wake on LAN signal gets send to the
        device with the given `mac_address` in case of a remote access.
        """
        info = self._action(
            'X_AVM-DE_GetAutoWakeOnLANByMACAddress', NewMACAddress=mac_address
        )
        return info['NewAutoWOLEnabled']

    def set_wakeonlan_status(self, mac_address, status=False):
        """
        Sets whether a wake on LAN signal should get send send to the
        device with the given `mac_address` in case of a remote access.
        `status` is a boolean, default value is `False`. This method has
        no return value.
        """
        args = {
            'NewMACAddress': mac_address,
            'NewAutoWOLEnabled': status,
        }
        self._action('X_AVM-DE_SetAutoWakeOnLANByMACAddress', arguments=args)

    def set_host_name(self, mac_address, name):
        """
        Sets the hostname of the device with the given `mac_address` to
        the new `name`.
        """
        args = {
            'NewMACAddress': mac_address,
            'NewHostName': name,
        }
        self._action('X_AVM-DE_SetHostNameByMACAddress', arguments=args)

    def run_host_update(self, mac_address):
        """
        Triggers the host with the given `mac_address` to run a system
        update. The method returns immediately, but for the device it
        take some time to do the OS update. All vendor warnings about running a
        system update apply, like not turning power off during a system
        update. So run this command with caution.
        """
        self._action('X_AVM-DE_HostDoUpdate', NewMACAddress=mac_address)
