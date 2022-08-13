import json

import pytest

from fritzconnection.core.devices import DeviceManager
from fritzconnection.core.processor import (
    Description,
    Device,
    SpecVersion,
    SystemVersion,
)


JSON_RESULT_TEST_SERIALIZE_DEVICE_01 = """{"device": {"device_attributes": {"UDN": "uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0", "UPC": null, "deviceType": "urn:schemas-upnp-org:device:InternetGatewayDevice:1", "friendlyName": "FRITZ!Box 7590", "manufacturer": "AVM Berlin", "manufacturerURL": "http://www.avm.de", "modelDescription": "FRITZ!Box 7590", "modelName": "FRITZ!Box 7590", "modelNumber": "avm", "modelURL": "http://www.avm.de", "presentationURL": "http://fritz.box"}, "device_services": []}, "specVersion": {"major": "1", "minor": "0"}, "systemVersion": {"HW": null, "Major": "154", "Minor": "7", "Patch": "29", "Buildnumber": null, "Display": "154.07.29"}}"""


def make_spec_version():
    spec_version = SpecVersion()
    spec_version.major = "1"
    spec_version.minor = "0"
    return spec_version


def make_system_version():
    system_version = SystemVersion()
    system_version.HW = None
    system_version.Major = "154"
    system_version.Minor = "7"
    system_version.Patch = "29"
    system_version.Buildnumber = None
    system_version.Display = "154.07.29"
    return system_version


def make_device():
    device = Device()
    device.deviceType = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"
    device.friendlyName = "FRITZ!Box 7590"
    device.manufacturer = "AVM Berlin"
    device.manufacturerURL = "http://www.avm.de"
    device.modelDescription = "FRITZ!Box 7590"
    device.modelName = "FRITZ!Box 7590"
    device.modelNumber = "avm"
    device.modelURL = "http://www.avm.de"
    device.UDN = "uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0"
    device.UPC = None
    device.presentationURL = "http://fritz.box"
    return device


def test_serialize_device_01():
    """
    build simple DeviceManager with a Description without Devices.
    """
    spec_version = make_spec_version()
    system_version = make_system_version()
    device = make_device()

    description = Description(root=[])  # suppress node processing
    description.device = device
    description.specVersion = spec_version
    description.systemVersion = system_version

    result = description.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SERIALIZE_DEVICE_01
    return result


def main():
    result = test_serialize_device_01()
    print(result)
    print()
    js = json.dumps(result)
    print(js)
    print()
    print(json.loads(js))

if __name__ == "__main__":
    main()
