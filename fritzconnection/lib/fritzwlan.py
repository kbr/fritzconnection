"""
Module to get informations about WLAN devices.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Bernd Strebel, Klaus Bremer


import itertools
from ..core.exceptions import FritzServiceError
from .fritzbase import AbstractLibraryBase


# important: don't set an extension number here:
SERVICE = 'WLANConfiguration'


class FritzWLAN(AbstractLibraryBase):
    """
    Class to list all known wlan devices. All parameters are optional.
    If given, they have the following meaning: `fc` is an instance of
    FritzConnection, `address` the ip of the Fritz!Box, `port` the port
    to connect to, `user` the username, `password` the password,
    `timeout` a timeout as floating point number in seconds, `use_tls` a
    boolean indicating to use TLS (default False). The *service*
    parameter specifies the configuration in use. Typically this is 1
    for 2.4 GHz, 2 for 5 GHz and 3 for a guest network. This can vary
    depending on the router model and change with future standards.
    """
    def __init__(self, *args, service=1, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = service

    def _action(self, actionname, **kwargs):
        service = f'{SERVICE}{self.service}'
        return self.fc.call_action(service, actionname, **kwargs)

    @property
    def host_number(self):
        """
        Number of registered wlan devices for the active
        WLANConfiguration.
        """
        result = self._action('GetTotalAssociations')
        return result['NewTotalAssociations']

    @property
    def total_host_number(self):
        """
        Total NewAssociatedDeviceIndexumber of registered wlan devices
        for all WLANConfigurations.
        """
        total = 0
        _service = self.service
        for service in itertools.count(1):
            self.service = service
            try:
                total += self.host_number
            except FritzServiceError:
                break
        self.service = _service
        return total


    @property
    def ssid(self):
        """The WLAN SSID"""
        result = self._action('GetSSID')
        return result['NewSSID']

    @ssid.setter
    def ssid(self, value):
        self._action('SetSSID', NewSSID=value)

    @property
    def channel(self):
        """The WLAN channel in use"""
        return self.channel_infos()['NewChannel']

    @property
    def alternative_channels(self):
        """Alternative channels (as string)"""
        return self.channel_infos()['NewPossibleChannels']

    def channel_infos(self):
        """
        Return a dictionary with the keys *NewChannel* and
        *NewPossibleChannels* indicating the active channel and
        alternative ones.
        """
        return self._action('GetChannelInfo')

    def set_channel(self, number):
        """
        Set a new channel. *number* must be a valid channel number for
        the active WLAN. (Valid numbers are listed by *alternative_channels*.)
        """
        self._action('SetChannel', NewChannel=number)

    def get_generic_host_entry(self, index):
        """
        Return a dictionary with informations about the device
        internally stored at the position 'index'.
        """
        result = self._action(
            'GetGenericAssociatedDeviceInfo',
            NewAssociatedDeviceIndex=index
        )
        return result

    def get_specific_host_entry(self, mac_address):
        """
        Return a dictionary with informations about the device
        with the given 'mac_address'.
        """
        result = self._action(
            'GetSpecificAssociatedDeviceInfo',
            NewAssociatedDeviceMACAddress=mac_address
        )
        return result

    def get_hosts_info(self):
        """
        Returns a list of dictionaries with information about the known hosts.
        The dict-keys are: 'auth', 'mac', 'ip', 'signal', 'speed'
        """
        informations = []
        for index in itertools.count():
            try:
                host = self.get_generic_host_entry(index)
            except IndexError:
                break
            informations.append({
                'service': self.service,
                'index': index,
                'status': host['NewAssociatedDeviceAuthState'],
                'mac': host['NewAssociatedDeviceMACAddress'],
                'ip': host['NewAssociatedDeviceIPAddress'],
                'signal': host['NewX_AVM-DE_SignalStrength'],
                'speed': host['NewX_AVM-DE_Speed']
            })
        return informations
