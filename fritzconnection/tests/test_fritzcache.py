import json

import pytest

from fritzconnection.core.devices import DeviceManager
from fritzconnection.core.processor import (
    Description,
    Device,
    Serializer,
    Service,
    SpecVersion,
    SystemVersion,
)


# some test data.
# data can be anything but take some real data from an existing router:

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

DATA_SERVICE_SERVICETYPE = "urn:dslforum-org:service:DeviceInfo:1"
DATA_SERVICE_SERVICEID = "urn:DeviceInfo-com:serviceId:DeviceInfo1"
DATA_SERVICE_CONTROLURL = "/upnp/control/deviceinfo"
DATA_SERVICE_EVENTSUBURL = "/upnp/control/deviceinfo"
DATA_SERVICE_SCPDURL = "/deviceinfoSCPD.xml"

JSON_RESULT_TEST_SERIALIZE_SPECVERSION = f"""{{"major": "{DATA_SPEC_MAJOR_VERSION}", "minor": "{DATA_SPEC_MINOR_VERSION}"}}"""

JSON_RESULT_TEST_SERIALIZE_SYSTEMVERSION = f"""{{"Buildnumber": null, "Display": "{DATA_SYS_DISPLAY}", "HW": null, "Major": "{DATA_SYS_MAJOR}", "Minor": "{DATA_SYS_MINOR}", "Patch": "{DATA_SYS_PATCH}"}}"""

JSON_RESULT_TEST_SERIALIZE_SERVICE = f"""{{"service_attributes": {{"SCPDURL": "{DATA_SERVICE_SCPDURL}", "controlURL": "{DATA_SERVICE_CONTROLURL}", "eventSubURL": "{DATA_SERVICE_EVENTSUBURL}", "serviceId": "{DATA_SERVICE_SERVICEID}", "serviceType": "{DATA_SERVICE_SERVICETYPE}"}}}}"""

JSON_RESULT_TEST_SERIALIZE_DEVICE_01 = f"""{{"device": {{"device_attributes": {{"UDN": "{DATA_DEVICE_UDN}", "UPC": null, "deviceType": "{DATA_DEVICE_DEVICETYPE}", "friendlyName": "{DATA_DEVICE_FRIENDLYNAME}", "manufacturer": "{DATA_DEVICE_MANUFACTURER}", "manufacturerURL": "{DATA_DEVICE_MANUFACTURERURL}", "modelDescription": "{DATA_DEVICE_MODELDESCRIPTION}", "modelName": "{DATA_DEVICE_MODELNAME}", "modelNumber": "{DATA_DEVICE_MODELNUMBER}", "modelURL": "{DATA_DEVICE_MODELURL}", "presentationURL": "{DATA_DEVICE_PRESENTATIONURL}"}}, "device_services": [], "device_devices": []}}, "specVersion": {{"major": "{DATA_SPEC_MAJOR_VERSION}", "minor": "{DATA_SPEC_MINOR_VERSION}"}}, "systemVersion": {{"Buildnumber": null, "Display": "{DATA_SYS_DISPLAY}", "HW": null, "Major": "{DATA_SYS_MAJOR}", "Minor": "{DATA_SYS_MINOR}", "Patch": "{DATA_SYS_PATCH}"}}}}"""


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


def make_service():
    service = Service()
    service.serviceType = DATA_SERVICE_SERVICETYPE
    service.serviceId = DATA_SERVICE_SERVICEID
    service.controlURL = DATA_SERVICE_CONTROLURL
    service.eventSubURL = DATA_SERVICE_EVENTSUBURL
    service.SCPDURL = DATA_SERVICE_SCPDURL
    return service


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


class Check(Serializer):
    """
    Simple Subclass for Serializer for testing.
    """
    def __init__(self, one=1, two=2):
        self.one = one
        self.two = two


def test_serializer():
    """
    Test the Serializer superclass.
    """
    check = Check()
    data = check.serialize()
    one_three = Check(one=3)
    assert check != one_three
    one_three.deserialize(data)
    assert check == one_three


def test_serializer_02():
    """
    Test for same set of attributes.
    """
    small = Check()
    big = Check()
    assert small == big
    assert big == small
    big.three = 3
    assert small != big
    assert big != small


def test_serialize_exclude():
    """
    Test Serializer superclass with exclude argument
    """
    check = Check()
    data = check.serialize(exclude=['one'])
    one_three = Check(one=3)
    assert check != one_three
    one_three.deserialize(data)
    assert check != one_three
    one_three.one = 1
    assert check == one_three


def test_serialize_spec_version():
    """
    Serialize a SpecVersion instance to json.
    """
    spec_version = make_spec_version()
    result = spec_version.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SERIALIZE_SPECVERSION


def test_deserialize_spec_version():
    """
    Deserialize a SpecVersion instance from json.
    """
    data = json.loads(JSON_RESULT_TEST_SERIALIZE_SPECVERSION)
    sv = SpecVersion()
    sv.deserialize(data)
    assert sv == make_spec_version()



def test_serialize_system_version():
    """
    Serialize a SystemVersion instance to json.
    """
    system_version = make_system_version()
    result = system_version.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SERIALIZE_SYSTEMVERSION


def test_deserialize_system_version():
    """
    Deserialize a SystemVersion instance from json.
    """
    system_version = make_system_version()
    data = json.loads(JSON_RESULT_TEST_SERIALIZE_SYSTEMVERSION)
    sv = SystemVersion()
    assert sv != system_version
    sv.deserialize(data)
    assert sv == system_version


def test_serialize_service():
    """
    Serialize a Service Instance.
    """
    service = make_service()
    result = service.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SERIALIZE_SERVICE


def test_deserialize_service():
    """
    Deserialize a Service Instance.
    """
    service = make_service()
    data = json.loads(JSON_RESULT_TEST_SERIALIZE_SERVICE)
    s = Service()
    assert s != service
    s.deserialize(data)
    assert s == service


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
