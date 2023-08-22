"""
Module to access home-automation devices by the TR-064 and the
AHA-HTTP-Interface.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


from __future__ import annotations

import datetime
import itertools
from warnings import warn
from xml.etree import ElementTree as etree

from .fritzbase import AbstractLibraryBase


# tr-064 homeautomation service
SERVICE = 'X_AVM-DE_Homeauto1'

# Constants describing the possible capabilities of a device.
# Values are bit positions in the AVM-FunctionBitMask:
HAN_FUN_UNIT_1 = 0
UNKNOWN_1= 1
LIGHT_BULB = 2
UNKNOWN_2 = 3
ALARM_SENSOR = 4
AVM_BUTTON = 5
RADIATOR_CONTROL = 6
ENERGY_SENSOR = 7
TEMPERATURE_SENSOR = 8
PLUGGABLE = 9
AVM_DECT_REPEATER = 10
MICROPHONE = 11
UNKNOWN_3 = 12
HAN_FUN_UNIT_2 = 13
UNKNOWN_4 = 14
SWITCHABLE = 15
ADJUSTABLE = 16
COLOR_BULB = 17
BLIND = 18
UNKNOWN_5 = 19
HUMIDITY_SENSOR = 20

# offset for removing the prefix "New" from the tr-064 avm-keys
KEY_OFFSET = len("New")


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
    def get_info(self) -> dict:
        """
        Return a dictionary with a single key-value pair:
        'NewAllowedCharsAIN': string with all allowed chars for state
        variable AIN
        """
        return self._action('GetInfo')

    def get_device_information_by_index(
        self,
        index: int
    ) -> dict:
        """
        Return a dictionary with all device arguments according to the
        AVM documentation (x_homeauto) at the given internal index.
        Raise a FritzArrayIndexError (subclass of IndexError) on invalid
        index values.
        """
        return self._action('GetGenericDeviceInfos', NewIndex=index)

    def get_device_information_by_identifier(
        self,
        identifier: str
    ) -> dict:
        """
        Returns a dictionary with all device arguments according to the
        AVM documentation (x_homeauto) with the given identifier (AIN).
        Raise an FritzArgumentError on invalid identifier.
        """
        return self._action('GetSpecificDeviceInfos', NewAIN=identifier)

    def device_informations(self) -> list[dict]:
        """
        .. deprecated:: 1.9.0
           Use :func:`get_device_information_list` instead.
        """
        warn('This method is deprecated. Use "get_device_information_list" instead.', DeprecationWarning)
        return self.get_device_information_list()

    def device_information(self) -> list[dict]:
        """
        .. deprecated:: 1.12.0
           Use :func:`get_device_information_list` instead.
        """
        warn('This method is deprecated. Use "get_device_information_list" instead.', DeprecationWarning)
        return self.get_device_information_list()

    def get_device_information_list(self) -> list[dict]:
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

    def get_homeautomation_device(
        self,
        identifier: str | None = None,
        index: int | None = None
    ) -> HomeAutomationDevice | None:
        """
        Returns a HomeAutomationDevice instance. The device can be
        identified by the `identifier` (ain) or the `index` in the
        internal router device list. If both arguments are given,
        `identifier` takes preference. If neither `identifier` nor
        `index` are given `None` gets returned.
        """
        if identifier:
            information = self.get_device_information_by_identifier(identifier)
        elif index:
            information = self.get_device_information_by_index(index)
        else:
            return None
        return HomeAutomationDevice(self, information, identifier)

    def get_homeautomation_devices(self) -> list[HomeAutomationDevice]:
        """
        Returns a list with HomeAutomationDevice instances of all known
        home-automation devices. The list is ordered in the way the
        router provided the data.
        """
        return [
            HomeAutomationDevice(self, information) for information
            in self.get_device_information_list()
        ]

    def set_switch(self, identifier: str, on: bool = True) -> None:
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


class HomeAutomationDevice:
    """
    Represents a device for homeautomation.

    `fh` is a FritzHomeAutomation instance. `device_information` is a
    dictionary like the ones returned from FritzHomeAutomation methods
    'get_device_information_by_index()',
    'get_device_information_by_identifier()' or an item from the list of
    dictionaries returned from 'get_device_information_list()'. This
    dictionary returned from the
    'get_device_information_by_identifier()' has no 'NewAIN' entry. In
    this case the argument `identifier` must be provided with the
    missing 'ain'. If both `identifier` is provided and
    `device_information` has a 'NewAIN' entry the latter takes
    preference.

    Instances will have the folloing dynamic created attributes:

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

    Depending on the device not all attributes will have a meaning.
    """
    def __init__(
        self,
        fh: FritzHomeAutomation,
        device_information: dict,
        identifier: str | None = None
    ):
        self.fh = fh
        self.AIN = identifier
        self._extraxt_device_information_as_attributes(device_information)

    def __repr__(self):
        """
        Provide some basic information about the device.
        """
        return f"ain: {self.AIN}, {self.Manufacturer} - {self.ProductName}"

    def _extraxt_device_information_as_attributes(self, device_information):
        """
        Takes the device_information, which is a dictionary returned
        from a call like
        'FritzHomeAutomation.get_device_information_by_index()' and
        updates the instance-attributes with the key-value pairs of this
        dictionary. The key-names are changed by stripping the prefix
        'New'. All keys updated by this automatic process are in
        MixedCase style - as provided from the router - while all other
        attributes are snake_case.
        """
        for key, value in device_information.items():
            self.__dict__[key[KEY_OFFSET:]] = value

    def _bitmatch(self, value: int) -> bool:
        """
        Returns a boolean whether the `value` bit is set in
        `self.FunctionBitMask`.
        """
        feature_bit = 1 << value
        return feature_bit & self.FunctionBitMask == feature_bit  # type: ignore

    def call_http(self, command: str, **kwargs) -> dict[str, str]:
        """
        Shortcut to access the http-interface of the router.

        Used to send a `command` with the given keyword-arguments to
        _this_ device. Raises a FritzHttpInterfaceError if the device
        does not support the command or arguments. On missing rights a
        FritzAuthorizationError is raised.
        """
        return self.fh.fc.call_http(command, self.identifier, **kwargs)

    @property
    def identifier(self) -> str:
        return self.AIN  # type: ignore

    @property
    def is_han_fun_unit(self) -> bool:
        return self._bitmatch(HAN_FUN_UNIT_1) or self._bitmatch(HAN_FUN_UNIT_2)

    @property
    def is_bulb(self) -> bool:
        return self._bitmatch(LIGHT_BULB)

    @property
    def is_alarm_sensor(self) -> bool:
        return self._bitmatch(ALARM_SENSOR)

    @property
    def is_avm_button(self) -> bool:
        return self._bitmatch(AVM_BUTTON)

    @property
    def is_radiator_control(self) -> bool:
        return self._bitmatch(RADIATOR_CONTROL)

    @property
    def is_energy_sensor(self) -> bool:
        return self._bitmatch(ENERGY_SENSOR)

    @property
    def is_temperature_sensor(self) -> bool:
        return self._bitmatch(TEMPERATURE_SENSOR)

    @property
    def is_pluggable(self) -> bool:
        return self._bitmatch(PLUGGABLE)

    @property
    def is_avm_dect_repeater(self) -> bool:
        return self._bitmatch(AVM_DECT_REPEATER)

    @property
    def is_microphone(self) -> bool:
        return self._bitmatch(MICROPHONE)

    @property
    def is_switchable(self) -> bool:
        return self._bitmatch(SWITCHABLE)

    @property
    def is_adjustable(self) -> bool:
        return self._bitmatch(ADJUSTABLE)

    @property
    def is_color_bulb(self) -> bool:
        return self._bitmatch(COLOR_BULB)

    @property
    def is_blind(self) -> bool:
        return self._bitmatch(BLIND)

    @property
    def is_humidity_sensor(self) -> bool:
        return self._bitmatch(HUMIDITY_SENSOR)

    def update_device_information(self) -> None:
        """
        Triggers the router to update the device dependent
        instance-attributes.
        """
        self._extraxt_device_information_as_attributes(
            self.fh.get_device_information_by_identifier(self.identifier)
        )

    def get_basic_device_stats(self) -> dict:
        """
        Returns a dictionary of device statistics. The content depends on
        the actors supported by a device. The keys can be:

        key:            on actor:
        temperature     temperature sensor
        humidity        humidity sensor
        voltage         energy sensor
        power           energy sensor
        energy          energy sensor

        The corresponding values are also dictionaries having a common
        structure:

        key:        value:
        count       int: number of data points
        grid        int: time resolution in seconds
        datatime    datetime: timestamp of last data update
        data        list of data points (integers)

        The application can inspect the keys or use the properties like
        `is_energy_sensor` to check for actors provided by the device.
        If the usecase is just about the actors and not the data, the
        properties are much(!) faster.
        """
        response = self.call_http("getbasicdevicestats")
        return self.extract_basicdevicestats_response(response)

    @staticmethod
    def extract_basicdevicestats_response(response: dict) -> dict:
        """
        Converts the xml `response` and returns a dictionary with a
        datastructure described in the method `get_basic_device_stats()`
        """
        # implemented separately for testing.
        # 'stats' and 'datatime' are defined in the AVM xml-protocol
        # some types are dynamic therefore some 'type: ignore'.
        elements = {}
        content = response['content']
        root = etree.fromstring(content)
        for element in root:
            content = {}
            stats: etree.Element | None = element.find("stats")
            if stats is None:
                continue
            for key, value in stats.attrib.items():
                value = int(value)  # type: ignore
                if key == "datatime":
                    value = datetime.datetime.fromtimestamp(value)  # type: ignore
                content[key] = value
            content["data"] = list(map(int, stats.text.split(",")))  # type: ignore
            elements[element.tag] = content
        return elements

    def get_switch_state(self) -> bool:
        """
        Returns a boolean indicating whether a switchable device is set
        to on (True) or off (False).
        """
        self.update_device_information()
        return self.SwitchState.lower() == 'on'  # type: ignore

    def set_switch(self, on: bool = True) -> None:
        """
        Set a switchable device to 'on' (True) or 'off' (False).
        """
        self.fh.set_switch(self.identifier, on)

