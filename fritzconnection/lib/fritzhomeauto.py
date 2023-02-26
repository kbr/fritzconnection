"""
Module to access home-automation devices
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import itertools
from warnings import warn

from .fritzbase import AbstractLibraryBase


# tr-064 homeautomation service
SERVICE = 'X_AVM-DE_Homeauto1'

# Constants describing the possible capabilities of a device.
# Values are bit positions.
HAN_FUN_UNIT_1 = 0
UNKNOWN_1= 1
LIGHT_BULB = 2
UNKNOWN = 3
ALARM_SENSOR = 4
AVM_BUTTON = 5
RADIATOR_CONTROL = 6
ENERGY_SENSOR = 7
TEMPERATURE_SENSOR = 8
PLUGGABLE = 9
AVM_DECT_REPEATER = 10
MICROPHONE = 11
UNKNOWN_2 = 12
HAN_FUN_UNIT_2 = 13
UNKNOWN_3 = 14
SWITCHABLE = 15
ADJUSTABLE = 16
COLOR_BULB = 17
BLIND = 18
UNKNOWN_4 = 19
HUMIDITY_SENSOR = 20


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
        .. deprecated:: 1.9.0
           Use :func:`device_information` instead.
        """
        warn('This method is deprecated. Use "device_information" instead.', DeprecationWarning)
        return self.device_information()

    def device_information(self):
        """
        Returns a list of dictionaries for all known homeauto-devices.
        """
        info = list()
        for n in itertools.count():
            try:
                device_information = self.get_device_information_by_index(n)
            except IndexError:
                break
            info.append(device_information)
        return info

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


class DeviceProperties:
    """
    Provides the properties of a device according to the
    device-functionbitmask.
    """
    def __init__(self, function_bit_mask):
        self.function_bit_mask = function_bit_mask

    def _bitmap(self, value):
        value = 2 ** value
        return (value & self.function_bit_mask) == value

    @property
    def is_han_fun_unit(self):
        return self._bitmap(HAN_FUN_UNIT_1) or self._bitmap(HAN_FUN_UNIT_2)

    @property
    def is_bulb(self):
        return self._bitmap(LIGHT_BULB)

    @property
    def is_alarm_sensor(self):
        return self._bitmap(ALARM_SENSOR)

    @property
    def is_avm_button(self):
        return self._bitmap(AVM_BUTTON)

    @property
    def is_radiator_control(self):
        return self._bitmap(RADIATOR_CONTROL)

    @property
    def is_energy_sensor(self):
        return self._bitmap(ENERGY_SENSOR)

    @property
    def is_temperature_sensor(self):
        return self._bitmap(TEMPERATURE_SENSOR)

    @property
    def is_pluggable(self):
        return self._bitmap(PLUGGABLE)

    @property
    def is_avm_dect_repeater(self):
        return self._bitmap(AVM_DECT_REPEATER)

    @property
    def is_microphone(self):
        return self._bitmap(MICROPHONE)

    @property
    def is_switchable(self):
        return self._bitmap(SWITCHABLE)

    @property
    def is_adjustable(self):
        return self._bitmap(ADJUSTABLE)

    @property
    def is_color_bulb(self):
        return self._bitmap(COLOR_BULB)

    @property
    def is_blind(self):
        return self._bitmap(BLIND)

    @property
    def is_humidity_sensor(self):
        return self._bitmap(HUMIDITY_SENSOR)


class HomeAutomationDevice(DeviceProperties):
    """
    Represents a device for homeautomation providing at subset from the DeviceKind attributes.

    Instances will have the folloing additional attributes:

        AIN
        DeviceId
        FunctionBitMask
        FirmwareVersion
        Manufacturer
        ProductName
        DeviceName
        Present
        MultimeterIsEnabled
        MultimeterIsValid
        MultimeterPower
        MultimeterEnergy
        TemperatureIsEnabled
        TemperatureIsValid
        TemperatureCelsius
        TemperatureOffset
        SwitchIsEnabled
        SwitchIsValid
        SwitchState
        SwitchMode
        SwitchLock
        HkrIsEnabled
        HkrIsValid
        HkrIsTemperature
        HkrSetVentilStatus
        HkrSetTemperature
        HkrReduceVentilStatus
        HkrReduceTemperature
        HkrComfortVentilStatus
        HkrComfortTemperature

    Not all attributes will have a meaning. For that HomeAutomationDevice inherits from DeviceProperties
    to provide all the `is_` properties based on the FunctionBitMask-flags.
    """
    def __init__(self, fh, identifier, device_information):
        self.fh = fh
        self.indentifier = identifier  # aka ain
        self._extraxt_device_information_as_attributes(device_information)
        super().__init__(self.FunctionBitMask)

    @property
    def identifier(self):
        return self.AIN

    def _extraxt_device_information_as_attributes(self, device_information):
        """
        Takes the device_information, which is a dcitionary returned from a call like
        FritzHomeAutomation.get_device_information_by_index() and updates the instance-attributes
        with the key-value pairs of this dictionary. The key-names are changed by stripping the
        leading 'New'. All keys updated by this automatoc process are named in MixedCase style,
        while all other attributes are snake_case.
        """
        offset = len("New")
        for key, value in device_information.items():
            self.__dict__[key[offset:]] = value

    def update_device_information(self):
        """

        """
        self._extraxt_device_information_as_attributes(
            self.fh.get_device_information_by_identifier(self.identifier)
        )
