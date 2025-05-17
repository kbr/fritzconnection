"""
Module to get information about WLAN devices.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Bernd Strebel, Klaus Bremer


from __future__ import annotations

import io
import itertools
import random
import string

from ..core.exceptions import FritzServiceError
from .fritzbase import AbstractLibraryBase

try:
    import segno.helpers
except ImportError:
    SEGNO_INSTALLED = False
else:
    SEGNO_INSTALLED = True

# important: don't set an extension number here:
SERVICE = 'WLANConfiguration'
DEFAULT_PASSWORD_LENGTH = 12
_QR_SECURITY_WPA = 'WPA'
_QR_SECURITY_WEP  = 'WEP'
_QR_SECURITY_NO_PASS = 'nopass'
_BEACONTYPE_TO_QR_SECURITY = {
    'WPA': _QR_SECURITY_WPA,
    '11i': _QR_SECURITY_WPA,
    'WPAand11i': _QR_SECURITY_WPA,
    'WPA3': _QR_SECURITY_WPA,
    '11iandWPA3': _QR_SECURITY_WPA,
    'Basic': _QR_SECURITY_WEP,
    'OWE': _QR_SECURITY_NO_PASS,
    'OWETrans': _QR_SECURITY_NO_PASS,
    'None': _QR_SECURITY_NO_PASS,
}


def _get_wifi_qr_code(instance, kind='svg', security=None, scale=4, border=0):
    """
    Returns a file-like object providing a bytestring representing a
    qr-code for wlan access. `instance` is a FritzWLAN or FritzGuestWLAN
    instance. `kind` describes the type of the qr-code. Supported types
    are: 'svg', 'png', 'pdf', 'text' and 'text-compact'. Default is 'svg'.

    This function is not intended to get called directly. Instead it is
    available as a method on FritzWLAN instances (as well as on
    subclasses like FritzGuestWLAN) if the third party package `segno`
    is installed.

    Consider `guest_wlan` is a FritzGuestWLAN instance, then the
    following code will return a file like object with the qr-code image
    data in png-format: ::

        stream = guest_wlan.get_wifi_qr_code(kind='png')

    The stream can get used anywhere, where a file like object is
    expected, i.e. writing the content to a file (Note: the suffix must
    match the kind of the qr-code format): ::

        with open('qr_code.png', 'wb') as fobj:
            fobj.write(stream.read())

    The stream can be printed out if qr-code is represented as text: ::

        stream = guest_wlan.get_wifi_qr_code(kind='text')
        print(stream.getvalue())

    If `segno` is not installed the call will trigger an
    AttributeError when called on an instance and a NameError when
    called directly.

    .. versionadded:: 1.9.0

    The parameters `security` and `hidden` allow to forward these
    informations to the `segno` library. `security` is `None` or a
    string like `WPA`. `hidden` is a boolean value indicating the
    visibility of the network .

    .. versionadded:: 1.9.1

    If the `security` is `None` (default) the beacontype of the network
    is used to set the WLAN-Type accordingly. If the value of `security`
    is something else, this value gets used.

    `scale` defines the size of the produced qr-code. Default value is 4.

    .. versionadded:: 1.10

    """
    if not security:
        # if beacon type is something unknown, assume a "no pass" connection:
        security = _BEACONTYPE_TO_QR_SECURITY.get(instance.beacontype,
                                                  _QR_SECURITY_NO_PASS)
    password = instance.get_password() if security != _QR_SECURITY_NO_PASS else None
    qr_code = segno.helpers.make_wifi(
        ssid=instance.ssid,
        password=password,
        security=security,
        hidden=instance.is_hidden
    )
    if kind in ['text', 'text-compact']:
        stream = io.StringIO()
        compact = kind != 'text'
        qr_code.terminal(out=stream, border=border, compact=compact)
    else:
        stream = io.BytesIO()
        qr_code.save(out=stream, kind=kind, scale=scale, border=border)
    stream.seek(0)
    return stream


def _qr_code_enabler(cls):
    """Classdecorator to inject qr-capabilities at import time."""
    if SEGNO_INSTALLED:
        cls.get_wifi_qr_code = _get_wifi_qr_code
    return cls


@_qr_code_enabler
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
    def host_number(self) -> int:
        """
        Number of registered wlan devices for the active
        WLANConfiguration.
        """
        result = self._action('GetTotalAssociations')
        return result['NewTotalAssociations']

    @property
    def total_host_number(self) -> int:
        """
        Total NewAssociatedDeviceIndexNumber of registered wlan devices
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
    def ssid(self) -> str:
        """The WLAN SSID"""
        result = self._action('GetSSID')
        return result['NewSSID']

    @ssid.setter
    def ssid(self, value: str) -> None:
        self._action('SetSSID', NewSSID=value)

    @property
    def beacontype(self) -> str:
        """
        Represents the beacontype for the network as string.
        At time of writing (OS 7.29) possible values are:
        `None, 11i, WPAand11i, 11iandWPA3` for the private WiFi-security
        settings and `None, 11i, 11iandWPA3, OWETrans` for the guest
        network.
        """
        return self.get_info()['NewBeaconType']

    @property
    def is_hidden(self) -> bool:
        """Returns True if the SSID hidden (not advertised through beacons)."""
        return not self._action('GetBeaconAdvertisement')['NewBeaconAdvertisementEnabled']

    @property
    def channel(self) -> int:
        """The WLAN channel in use"""
        return self.channel_info()['NewChannel']

    @property
    def alternative_channels(self) -> str:
        """Alternative channels (as string)"""
        return self.channel_info()['NewPossibleChannels']

    def channel_info(self) -> dict:
        """
        Return a dictionary with the keys *NewChannel* and
        *NewPossibleChannels* indicating the active channel and
        alternative ones.
        """
        return self._action('GetChannelInfo')

    def set_channel(self, number: int) -> None:
        """
        Set a new channel. *number* must be a valid channel number for
        the active WLAN. (Valid numbers are listed by *alternative_channels*.)
        """
        self._action('SetChannel', NewChannel=number)

    def get_generic_host_entry(self, index: int) -> dict:
        """
        Return a dictionary with information about the device
        internally stored at the position 'index'.
        """
        result = self._action(
            'GetGenericAssociatedDeviceInfo',
            NewAssociatedDeviceIndex=index
        )
        return result

    def get_specific_host_entry(self, mac_address: str) -> dict:
        """
        Return a dictionary with information about the device
        with the given 'mac_address'.
        """
        result = self._action(
            'GetSpecificAssociatedDeviceInfo',
            NewAssociatedDeviceMACAddress=mac_address
        )
        return result

    def get_hosts_info(self) -> list[dict]:
        """
        Returns a list of dictionaries with information about the known
        hosts. The dict-keys are: 'service', 'index', 'status', 'mac',
        'ip', 'signal', 'speed'
        """
        information = []
        for index in itertools.count():
            try:
                host = self.get_generic_host_entry(index)
            except IndexError:
                break
            information.append({
                'service': self.service,
                'index': index,
                'status': host['NewAssociatedDeviceAuthState'],
                'mac': host['NewAssociatedDeviceMACAddress'],
                'ip': host['NewAssociatedDeviceIPAddress'],
                'signal': host['NewX_AVM-DE_SignalStrength'],
                'speed': host['NewX_AVM-DE_Speed']
            })
        return information

    def get_info(self) -> dict:
        """
        Returns a dictionary with general internal information about
        the current wlan network according to the AVM documentation.
        """
        return self._action("GetInfo")

    @property
    def is_enabled(self) -> bool:
        """Returns whether the network is enabled."""
        return self.get_info()["NewEnable"]

    def enable(self) -> None:
        """Enables the associated network."""
        self._set_enable(True)

    def disable(self) -> None:
        """Disables the associated network."""
        self._set_enable(False)

    def _set_enable(self, status):
        """Helper function for enable|disable."""
        self._action("SetEnable", arguments={"NewEnable": status})

    def get_password(self) -> str:
        """Returns the current password of the associated wlan."""
        return self._action("GetSecurityKeys")["NewKeyPassphrase"]

    def set_password(
        self,
        password: str | None = None,
        length: int = DEFAULT_PASSWORD_LENGTH
    ) -> None:
        """
        Sets a new password for the associated wlan.
        If no password is given a new one is created with the given
        length (the new password can get read with a subsequent call of
        `get_password`). Also creates a new pre-shared key.
        """
        preshared_key = self._create_preshared_key()
        password = password or self._create_password(length)
        arguments = {
            "NewKeyPassphrase": password,
            "NewPreSharedKey": preshared_key,
            "NewWEPKey0": "",
            "NewWEPKey1": "",
            "NewWEPKey2": "",
            "NewWEPKey3": "",
        }
        self._action("SetSecurityKeys", arguments=arguments)

    def _create_preshared_key(self):
        """
        Returns a new pre-shared key for setting a new password.
        The sequence is of uppercase characters as this is default on FritzOS
        at time of writing.
        """
        info = self.get_info()
        characters = info["NewAllowedCharsPSK"]
        length = info["NewMaxCharsPSK"]
        return "".join(random.choices(characters, k=length)).upper()

    @staticmethod
    def _create_password(length):
        """
        Returns a human-readable password with the given length.
        """
        # add just two human-readable special characters.
        # password strength increases with the length.
        # character permutations are: 64**length
        characters = string.ascii_letters + string.digits + "@#"
        return "".join(random.choices(characters, k=length))


class FritzGuestWLAN(FritzWLAN):
    """
    Inherits from FritzWLAN and provides all the same methods but for
    the guest network. On devices not providing a guest network this
    class will not fail, but handle the wlan network with the highest
    internal service number (which is by default the guest network on
    guest network providing devices).

    All parameters are optional. If given, they have the following
    meaning: `fc` is an instance of FritzConnection, `address` the ip of
    the Fritz!Box, `port` the port to connect to, `user` the username,
    `password` the password, `timeout` a timeout as floating point
    number in seconds, `use_tls` a boolean indicating to use TLS
    (default False).
    """
    def __init__(self, *args, **kwargs):
        """
        Initialize the guest wlan instance. All parameters are
        optional. If given, they have the following meaning: `fc` is an
        instance of FritzConnection, `address` the ip of the Fritz!Box,
        `port` the port to connect to, `user` the username, `password`
        the password, `timeout` a timeout as floating point number in
        seconds, `use_tls` a boolean indicating to use TLS (default
        False).
        """
        super().__init__(*args, **kwargs)
        for n in itertools.count(1):
            service = self.fc.services.get(f"{SERVICE}{n}")
            if service is None:
                self.service = n - 1
                break
