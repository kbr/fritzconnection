import json

import pytest

from fritzconnection.core.devices import DeviceManager
from fritzconnection.core.processor import (
    Description,
    Device,
    SpecVersion,
    SystemVersion,
)


DATA_SPEC_MAJOR_VERSION = "1"
DATA_SPEC_MINOR_VERSION = "0"

DATA_SYS_MAJOR = "154"
DATA_SYS_MINOR = "7"
DATA_SYS_PATCH = "29"
DATA_SYS_DISPLAY = "154.07.29"

DATA_DEVICE_DEVICETYPE = "urn:schemas-upnp-org:device:InternetGatewayDevice:1"
DATA_DEVICE_FRIENDLYNAME = "FRITZ!Box 7590"
DATA_DEVICE_MANUFACTURER = "AVM Berlin"
DATA_DEVICE_MANUFACTURERURL = "http://www.avm.de"
DATA_DEVICE_MODELDESCRIPTION = "FRITZ!Box 7590"
DATA_DEVICE_MODELNAME = "FRITZ!Box 7590"
DATA_DEVICE_MODELNUMBER = "avm"
DATA_DEVICE_MODELURL = "http://www.avm.de"
DATA_DEVICE_PRESENTATIONURL = "http://fritz.box"
DATA_DEVICE_UDN = "uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0"

JSON_RESULT_TEST_SERIALIZE_SPECVERSION = f"""{{"major": "{DATA_SPEC_MAJOR_VERSION}", "minor": "{DATA_SPEC_MINOR_VERSION}"}}"""

JSON_RESULT_TEST_SYSTEMVERSION = f"""{{"HW": null, "Major": "{DATA_SYS_MAJOR}", "Minor": "{DATA_SYS_MINOR}", "Patch": "{DATA_SYS_PATCH}", "Buildnumber": null, "Display": "{DATA_SYS_DISPLAY}"}}"""

JSON_RESULT_TEST_SERIALIZE_DEVICE_01 = f"""{{"device": {{"device_attributes": {{"UDN": "{DATA_DEVICE_UDN}", "UPC": null, "deviceType": "{DATA_DEVICE_DEVICETYPE}", "friendlyName": "{DATA_DEVICE_FRIENDLYNAME}", "manufacturer": "{DATA_DEVICE_MANUFACTURER}", "manufacturerURL": "{DATA_DEVICE_MANUFACTURERURL}", "modelDescription": "{DATA_DEVICE_MODELDESCRIPTION}", "modelName": "{DATA_DEVICE_MODELNAME}", "modelNumber": "{DATA_DEVICE_MODELNUMBER}", "modelURL": "{DATA_DEVICE_MODELURL}", "presentationURL": "{DATA_DEVICE_PRESENTATIONURL}"}}, "device_services": []}}, "specVersion": {{"major": "{DATA_SPEC_MAJOR_VERSION}", "minor": "{DATA_SPEC_MINOR_VERSION}"}}, "systemVersion": {{"HW": null, "Major": "{DATA_SYS_MAJOR}", "Minor": "{DATA_SYS_MINOR}", "Patch": "{DATA_SYS_PATCH}", "Buildnumber": null, "Display": "{DATA_SYS_DISPLAY}"}}}}"""


def make_spec_version():
    spec_version = SpecVersion()
    spec_version.major = DATA_SPEC_MAJOR_VERSION
    spec_version.minor = DATA_SPEC_MINOR_VERSION
    return spec_version


def make_system_version():
    system_version = SystemVersion()
    system_version.HW = None
    system_version.Major = DATA_SYS_MAJOR
    system_version.Minor = DATA_SYS_MINOR
    system_version.Patch = DATA_SYS_PATCH
    system_version.Buildnumber = None
    system_version.Display = DATA_SYS_DISPLAY
    return system_version


def make_device():
    device = Device()
    device.deviceType = DATA_DEVICE_DEVICETYPE
    device.friendlyName = DATA_DEVICE_FRIENDLYNAME
    device.manufacturer = DATA_DEVICE_MANUFACTURER
    device.manufacturerURL = DATA_DEVICE_MANUFACTURERURL
    device.modelDescription = DATA_DEVICE_MODELDESCRIPTION
    device.modelName = DATA_DEVICE_MODELNAME
    device.modelNumber = DATA_DEVICE_MODELNUMBER
    device.modelURL = DATA_DEVICE_MODELURL
    device.UDN = DATA_DEVICE_UDN
    device.UPC = None
    device.presentationURL = DATA_DEVICE_PRESENTATIONURL
    return device


def test_serialize_spec_version():
    spec_version = make_spec_version()
    result = spec_version.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SERIALIZE_SPECVERSION


def test_serialize_system_version():
    system_version = make_system_version()
    result = system_version.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SYSTEMVERSION


def test_serialize_device_01():
    """
    Serialize a simple DeviceManager with a Description and one Device
    but no services to json format.
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


def x_test_reload_device_01():
    """
    Reoad a simple DeviceManager with a Description and one Device
    but no services from json format.
    """



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
