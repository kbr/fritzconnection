"""
tests for serialization and deserialization data from the processor classes.
"""

import json

import pytest

from fritzconnection.core.processor import (
    Action,
    Argument,
    Description,
    Device,
    Scpd,
    Serializer,
    Service,
    SpecVersion,
    StateVariable,
    SystemVersion,
    ValueRange,
)


# some test data.
# data can be anything but take some real data from an existing router:

DATA_SPEC_MAJOR_VERSION = "1"
DATA_SPEC_MINOR_VERSION = "0"

DATA_SYS_MAJOR = "154"
DATA_SYS_MINOR = "7"
DATA_SYS_PATCH = "29"
DATA_SYS_DISPLAY = "154.07.29"

DATA_ARGUMENT_NAME = "NewManufacturerName"
DATA_ARGUMENT_DIRECTION = "out"
DATA_ARGUMENT_RELATEDSTATEVARIABLE = "ManufacturerName"

DATA_ACTION_NAME = "GetInfo"

DATA_VALUERANGE_MINIMUM = None
DATA_VALUERANGE_MAXIMUM = None
DATA_VALUERANGE_STEP = "1"  # for not having all the default values

DATA_STATEVARIABLE_NAME = "LastConnectionError"
DATA_STATEVARIABLE_DATATYPE = "string"
DATA_STATEVARIABLE_DEFAULTVALUE = "ERROR_NONE"
DATA_STATEVARIABLE_ALLOWED_VALUES = ["ERROR_NONE", "ERROR_ISP_TIME_OUT", "ERROR_COMMAND_ABORTED"]

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
JSON_RESULT_TEST_SERIALIZE_ARGUMENT = f"""{{"direction": "{DATA_ARGUMENT_DIRECTION}", "name": "{DATA_ARGUMENT_NAME}", "relatedStateVariable": "{DATA_ARGUMENT_RELATEDSTATEVARIABLE}"}}"""
JSON_RESULT_TEST_SERIALIZE_VALUERANGE = f"""{{"maximum": null, "minimum": null, "step": "{DATA_VALUERANGE_STEP}"}}"""
JSON_RESULT_TEST_SERIALIZE_ACTION = f"""{{"name": "{DATA_ACTION_NAME}", "arguments": [{JSON_RESULT_TEST_SERIALIZE_ARGUMENT}, {JSON_RESULT_TEST_SERIALIZE_ARGUMENT}]}}"""

# weird but f-strings substitute lists of strings different than json.dumps:
JSON_RESULT_TEST_SERIALIZE_STATEVARIABLE = f"""{{"attributes": {{"allowed_values": """ + json.dumps(DATA_STATEVARIABLE_ALLOWED_VALUES) + f""", "dataType": "{DATA_STATEVARIABLE_DATATYPE}", "defaultValue": "{DATA_STATEVARIABLE_DEFAULTVALUE}", "name": "{DATA_STATEVARIABLE_NAME}"}}, "allowedValueRange": {JSON_RESULT_TEST_SERIALIZE_VALUERANGE}}}"""
JSON_RESULT_TEST_SERIALIZE_SCPD = f"""{{"actions": [{JSON_RESULT_TEST_SERIALIZE_ACTION}, {JSON_RESULT_TEST_SERIALIZE_ACTION}], "specVersion": {JSON_RESULT_TEST_SERIALIZE_SPECVERSION}, "state_variables": [{JSON_RESULT_TEST_SERIALIZE_STATEVARIABLE}, {JSON_RESULT_TEST_SERIALIZE_STATEVARIABLE}]}}"""
JSON_RESULT_TEST_SERIALIZE_SERVICE = f"""{{"attributes": {{"SCPDURL": "{DATA_SERVICE_SCPDURL}", "controlURL": "{DATA_SERVICE_CONTROLURL}", "eventSubURL": "{DATA_SERVICE_EVENTSUBURL}", "serviceId": "{DATA_SERVICE_SERVICEID}", "serviceType": "{DATA_SERVICE_SERVICETYPE}"}}, "scpd": {JSON_RESULT_TEST_SERIALIZE_SCPD}}}"""
JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC = f"""{{"attributes": {{"UDN": "{DATA_DEVICE_UDN}", "UPC": null, "deviceType": "{DATA_DEVICE_DEVICETYPE}", "friendlyName": "{DATA_DEVICE_FRIENDLYNAME}", "manufacturer": "{DATA_DEVICE_MANUFACTURER}", "manufacturerURL": "{DATA_DEVICE_MANUFACTURERURL}", "modelDescription": "{DATA_DEVICE_MODELDESCRIPTION}", "modelName": "{DATA_DEVICE_MODELNAME}", "modelNumber": "{DATA_DEVICE_MODELNUMBER}", "modelURL": "{DATA_DEVICE_MODELURL}", "presentationURL": "{DATA_DEVICE_PRESENTATIONURL}"}}"""
JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC_SERVICE = f""", "services": [{JSON_RESULT_TEST_SERIALIZE_SERVICE}, {JSON_RESULT_TEST_SERIALIZE_SERVICE}]}}"""
JSON_RESULT_TEST_SERIALIZE_DEVICE = JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC + f""", "devices": [], "services": []}}"""
JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES = JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC + ', "devices": []' + JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC_SERVICE

# subdevices don't provide services and further devices
JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES_AND_SUBDEVICES = JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC + f""", "devices": [{JSON_RESULT_TEST_SERIALIZE_DEVICE}, {JSON_RESULT_TEST_SERIALIZE_DEVICE}]""" + JSON_RESULT_TEST_SERIALIZE_DEVICE_BASIC_SERVICE

JSON_RESULT_TEST_SERIALIZE_DESCRIPTION = f"""{{"device": {JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES_AND_SUBDEVICES}, "specVersion": {JSON_RESULT_TEST_SERIALIZE_SPECVERSION}, "systemVersion": {JSON_RESULT_TEST_SERIALIZE_SYSTEMVERSION}}}"""
# JSON_RESULT_TEST_SERIALIZE_DESCRIPTION = f"""{{"systemVersion": {JSON_RESULT_TEST_SERIALIZE_SYSTEMVERSION}}}"""


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


def make_argument():
    argument = Argument()
    argument.name = DATA_ARGUMENT_NAME
    argument.direction = DATA_ARGUMENT_DIRECTION
    argument.relatedStateVariable = DATA_ARGUMENT_RELATEDSTATEVARIABLE
    return argument


def make_valuerange():
    valuerange = ValueRange()
    valuerange.minimum = DATA_VALUERANGE_MINIMUM
    valuerange.maximum = DATA_VALUERANGE_MAXIMUM
    valuerange.step = DATA_VALUERANGE_STEP
    return valuerange


def make_action():
    # an Action has a name and a list of arguments.
    # make an Action with two arguments.
    action = Action()
    action.name = DATA_ACTION_NAME
    action._arguments.append(make_argument())
    action._arguments.append(make_argument())
    return action


def make_statevariable():
    # a StateVariable has a name like 'WANAccessType'
    # a dataType like 'string' or 'ui2'
    # a defaultValue
    # a list of strings of allowed_values like 'DSL', 'Cable' etc.
    # an allowedValueRange
    # Not all Atrributes must be defined.
    statevariable = StateVariable()
    statevariable.name = DATA_STATEVARIABLE_NAME
    statevariable.dataType = DATA_STATEVARIABLE_DATATYPE
    statevariable.defaultValue = DATA_STATEVARIABLE_DEFAULTVALUE
    statevariable.allowed_values = DATA_STATEVARIABLE_ALLOWED_VALUES
    statevariable.allowedValueRange = make_valuerange()
    return statevariable


def make_scpd():
    # a service control point definition has a list of Actions,
    # a list of StateVariables and a SpecVersion.
    scpd = Scpd(root=[])
    scpd._actions = [make_action(), make_action()]
    scpd._state_variables = [make_statevariable(), make_statevariable()]
    scpd.specVersion = make_spec_version()
    return scpd


def make_service():
    service = Service()
    service._scpd = make_scpd()
    service.serviceType = DATA_SERVICE_SERVICETYPE
    service.serviceId = DATA_SERVICE_SERVICEID
    service.controlURL = DATA_SERVICE_CONTROLURL
    service.eventSubURL = DATA_SERVICE_EVENTSUBURL
    service.SCPDURL = DATA_SERVICE_SCPDURL
    return service


def make_device(with_services=True, with_subdevices=True):
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
    if with_services:
        device._services = [make_service(), make_service()]
    if with_subdevices:
        device.devices = [
            make_device(with_services=False, with_subdevices=False),
            make_device(with_services=False, with_subdevices=False)
        ]
    return device


def make_description():
    description = Description(root=[])
    description.device = make_device()
    description.specVersion = make_spec_version()
    description.systemVersion = make_system_version()
    return description


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


def test_serialize_argument():
    """Serialize an Argument to json."""
    argument = make_argument()
    result = argument.serialize()
    json_result = json.dumps(result)
    assert json_result == JSON_RESULT_TEST_SERIALIZE_ARGUMENT


def test_deserialize_argument():
    """Deserialize an Argument from json."""
    argument = make_argument()
    data = json.loads(JSON_RESULT_TEST_SERIALIZE_ARGUMENT)
    a = Argument()
    assert a != argument
    a.deserialize(data)
    assert a == argument


def test_serialize_valuerange():
    """Serialize a ValueRange to json."""
    valuerange = make_valuerange()
    result = json.dumps(valuerange.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_VALUERANGE


def test_deserialize_valuerange():
    """Deserialize a ValueRange from json."""
    valuerange = make_valuerange()
    vr = ValueRange()
    assert vr != valuerange
    vr.deserialize(json.loads(JSON_RESULT_TEST_SERIALIZE_VALUERANGE))
    assert vr == valuerange


def test_serialize_action():
    """
    Serialize an Action with a name and two Argument instances in
    _arguments
    """
    action = make_action()
    result = json.dumps(action.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_ACTION


def test_deserialize_action():
    """
    Deerialize an Action with a name and two Argument instances in
    _arguments from json.
    """
    action = make_action()
    ac = Action()
    ac.deserialize(json.loads(JSON_RESULT_TEST_SERIALIZE_ACTION))
    assert ac == action


def test_serialize_statevariable():
    statevariable = make_statevariable()
    result = json.dumps(statevariable.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_STATEVARIABLE


def test_deserialize_statevariable():
    statevariable = make_statevariable()
    sv = StateVariable()
    assert sv != statevariable
    sv.deserialize(json.loads(JSON_RESULT_TEST_SERIALIZE_STATEVARIABLE))
    assert sv == statevariable


def test_serialize_scpd():
    scpd = make_scpd()
    result = json.dumps(scpd.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_SCPD


def test_deserialize_scpd():
    scpd = make_scpd()
    s = Scpd(root=[])
    s.deserialize(json.loads(JSON_RESULT_TEST_SERIALIZE_SCPD))
    assert s == scpd


def test_serialize_service():
    """
    Serialize a Service Instance.
    """
    service = make_service()
    result = json.dumps(service.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_SERVICE


def test_deserialize_service():
    """
    Deserialize a Service Instance.
    """
    service = make_service()
    data = json.loads(JSON_RESULT_TEST_SERIALIZE_SERVICE)
    s = Service()
    s.deserialize(data)
    assert s == service


def test_serialize_device():
    device = make_device(with_services=False, with_subdevices=False)
    result = json.dumps(device.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_DEVICE


def test_deserialize_device():
    device = make_device(with_services=False, with_subdevices=False)
    d = Device()
    d.deserialize(json.loads(JSON_RESULT_TEST_SERIALIZE_DEVICE))
    assert d == device


def test_serialize_device_with_services():
    device = make_device(with_services=True, with_subdevices=False)
    result = json.dumps(device.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES


def test_deserialize_device_with_services():
    device = make_device(with_services=True, with_subdevices=False)
    d = Device()
    d.deserialize(json.loads(JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES))
    assert d == device


def test_serialize_device_with_services_and_subdevices():
    device = make_device(with_services=True, with_subdevices=True)
    result = json.dumps(device.serialize())
    assert (
        result == JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES_AND_SUBDEVICES
    )

def test_deserialize_device_with_services_and_subdevices():
    device = make_device(with_services=True, with_subdevices=True)
    d = Device()
    d.deserialize(
        json.loads(
            JSON_RESULT_TEST_SERIALIZE_DEVICE_WITH_SERVICES_AND_SUBDEVICES
        )
    )
    assert d == device


def test_serialize_description():
    description = make_description()
    result = json.dumps(description.serialize())
    assert result == JSON_RESULT_TEST_SERIALIZE_DESCRIPTION


def test_deserialize_description():
    description = make_description()
    data = json.loads(JSON_RESULT_TEST_SERIALIZE_DESCRIPTION)
    d = Description(root=[])
    d.deserialize(data)
    assert d == description
    d = Description.from_data(data)
    assert d == description
