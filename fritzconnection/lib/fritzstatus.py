"""
Module to read status-information from a FritzBox.
Since v2.0 this module is mainly a glue-module for backward compatibility.
"""
import datetime
from dataclasses import field

from fritzconnection import FritzConnection
from fritzconnection.core.description import DeviceLog
from fritzconnection.core.utils import get_xml_root
from fritzconnection.lib.fritztools import ArgumentNamespace


class FritzStatus:
    """
    Class for providing status-information about the device and WAN connections
    """
    
    def __init__(self, fc=None, **kwargs):
        if fc is None:
            fc = FritzConnection(**kwargs)
        self.fc = fc

    @property
    def has_wan_support(self) -> bool:
        """
        True if the device supports a WAN interface.
        False otherwise.
        """
        return self.fc.has_wan_support

    @property
    def update_available(self) -> str:
        """
        The new version number (as a string) if an update is available or an
        empty string if no update is avilable.
        """
        return self.fc.call_action("UserInterface1", "GetInfo")["NewX_AVM-DE_Version"]

    def get_device_info(self) -> ArgumentNamespace:
        """
        Returns an ArgumentNamespace with the attributes:

        manufacturer_name, manufacturer_oui, model_name, description,
        product_class, serial_number, software_version, hardware_version,
        spec_version, provisioning_code, up_time, device_log

        .. versionadded:: 1.10

        """
        return ArgumentNamespace(self.fc.call_action("DeviceInfo1", "GetInfo"))
        
    def get_device_log(self, filter: str | None = None) -> DeviceLog:
        """
        The device log is a list of events with the attributes `id`,
        `group`, `date`, `time` and `msg` holding information like "DSL
        synchronization starting (training)" and other system messages.
        The Method returns a DeviceLog instance holding a list of Event
        instances. The DeviceLog instance is an iterable and can be
        used on a FritzStatus instance like:

        >>> device_log = fritzstatus.get_avm_device_log()
        >>> for event in device_log:
        >>>     print(event.datetime, event.msg)

        The returned events can be filtered by groups like 'sys', 'net',
        'fon', 'wlan' or 'usb'. To filter by a group provide the
        group-name as filter-argument.
        """
        result = self.fc.call_action("DeviceInfo1", "X_AVM-DE_GetDeviceLogPath")
        path = result["NewDeviceLogPath"]
        if filter:
            path = f"{path}&filter={filter}"
        url = f"{self.fc.address}{path}"
        root_node = get_xml_root(url, session=self.fc.session)
        device_log = DeviceLog()
        device_log.load(root_node)
        return device_log

    def get_avm_device_log(self, filter: str | None = None) -> DeviceLog:
        """
        Alias for backward compatibility.
        
        .. version-deprecated:: 2.0
           Use :py:func:`get_device_log` instead.
        """
        return self.get_device_log(filter)
