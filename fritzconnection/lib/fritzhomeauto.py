"""
Modul to access home-automation devices
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import itertools
from .fritzbase import AbstractLibraryBase


SERVICE = 'X_AVM-DE_Homeauto1'


class FritzHomeAutomation(AbstractLibraryBase):
    """
    Interface for fritzbox homeauto service. All parameters are
    optional. If given, they have the following meaning: `fc` is an
    instance of FritzConnection, `address` the ip of the Fritz!Box,
    `port` the port to connect to, `user` the username, `password` the
    password, `timeout` a timeout as floating point number in seconds,
    `use_tls` a boolean indicating to use TLS (default False).
    """

    def _action(self, actionname, *, arguments=None, **kwargs):
        if arguments is None:
            arguments = kwargs
        return self.fc.call_action(SERVICE, actionname, arguments=arguments)

    @property
    def get_info(self):
        """
        Return a dictionary with a single key-value pair:
        'NewAllowedCharsAIN': string with all allowed chars for state
        variable AIN
        """
        return self._action('GetInfo')

    def get_device_information_by_index(self, index):
        """
        Return a dictionary with all device arguments according to the
        AVM documentation (x_homeauto) at the given internal index.
        Raise a FritzArrayIndexError (subclass of IndexError) on invalid
        index values.
        """
        return self._action('GetGenericDeviceInfos', NewIndex=index)

    def get_device_information_by_identifier(self, identifier):
        """
        Returns a dictionary with all device arguments according to the
        AVM documentation (x_homeauto) with the given identifier (AIN).
        Raise an FritzArgumentError on invalid identifier.
        """
        return self._action('GetSpecificDeviceInfos', NewAIN=identifier)

    def device_informations(self):
        """
        Returns a list of dictionaries for all known homeauto-devices.
        """
        infos = list()
        for n in itertools.count():
            try:
                info = self.get_device_information_by_index(n)
            except IndexError:
                break
            infos.append(info)
        return infos

    def set_switch(self, identifier, on=True):
        """
        Sets a switch state on devices providing a switch state.
        'identifier' must be the AIN of the device. 'on' is a boolean
        whether the switch should be on (True) or off (False).
        This method has no return value.
        Raise a FritzArgumentError on invalid identifier.
        """
        arguments = {
            'NewAIN': identifier,
            'NewSwitchState': 'ON' if on else 'OFF'
        }
        self._action('SetSwitch', arguments=arguments)
