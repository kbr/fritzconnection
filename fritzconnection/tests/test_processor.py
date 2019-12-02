
import os
import pytest

from ..core.processor import (
    Description,
    Device,
    Service,
    Scpd,
)
from ..core.utils import get_xml_root


@pytest.fixture()
def igddesc_source(datadir):
    os.chdir(datadir)
    return get_xml_root('igddesc.xml')


@pytest.fixture()
def tr64desc_source(datadir):
    os.chdir(datadir)
    return get_xml_root('tr64desc.xml')


@pytest.fixture()
def igdconn_scpd_source(datadir):
    os.chdir(datadir)
    return get_xml_root('igdconnSCPD.xml')


@pytest.fixture()
def scpd_instance(igdconn_scpd_source):
    return Scpd(igdconn_scpd_source)


@pytest.mark.parametrize(
    "attribute, value", [
        ('spec_version', '1.0'),
        ('device_model_name', 'FRITZ!Box 7590'),
    ])
def test_igd_description_specversion(attribute, value, igddesc_source):
    d = Description(igddesc_source)
    assert d.spec_version == '1.0'


@pytest.mark.parametrize(
    "attribute, value", [
        ('deviceType', 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'),
        ('friendlyName', 'FRITZ!Box 7590'),
        ('manufacturer', 'AVM Berlin'),
        ('manufacturerURL', 'http://www.avm.de'),
        ('modelDescription', 'FRITZ!Box 7590'),
        ('modelName', 'FRITZ!Box 7590'),
        ('modelNumber', 'avm'),
        ('modelURL', 'http://www.avm.de'),
        ('UDN', 'uuid:75802409-bccb-just-a-test-udn'),
    ])
def test_igd_device(attribute, value, igddesc_source):
    d = Description(igddesc_source)
    device = d.device
    assert getattr(device, attribute) == value


def test_igd_device_services(igddesc_source):
    # the device should have one service instance in services.
    d = Description(igddesc_source)
    services = d.device._services
    assert len(services) == 1
    assert isinstance(services[0], Service)


@pytest.mark.parametrize(
    "attribute, value", [
        ('serviceType', 'urn:schemas-any-com:service:Any:1'),
        ('serviceId', 'urn:any-com:serviceId:any1'),
        ('controlURL', '/igdupnp/control/any'),
        ('eventSubURL', '/igdupnp/control/any'),
        ('SCPDURL', '/any.xml'),
    ])
def test_igd_device_service(attribute, value, igddesc_source):
    d = Description(igddesc_source)
    service = d.device._services[0]
    assert getattr(service, attribute) == value


def test_igd_device_service_name(igddesc_source):
    """
    Every service has a name. First (and only) service of the main
    device has the name 'any1'.
    """
    d = Description(igddesc_source)
    service = d.device._services[0]
    assert service.name == 'any1'


def test_igd_device_devices(igddesc_source):
    # the device should have one device instance in devices.
    d = Description(igddesc_source)
    devices = d.device.devices
    assert len(devices) == 1
    assert isinstance(devices[0], Device)


def test_idg_nested_services_part1(igddesc_source):
    """
    The main device should have a sub-device with another subdevice. The
    first sub-device should have a sublist with one service.
    """
    d = Description(igddesc_source)
    sub_device = d.device.devices[0]
    assert len(sub_device._services) == 1


def test_idg_nested_services_part2(igddesc_source):
    """
    The main device should have a sub-device with another subdevice. The
    sub-sub-device should have a sublist with three service.
    """
    d = Description(igddesc_source)
    sub_device = d.device.devices[0].devices[0]
    assert len(sub_device._services) == 3


@pytest.mark.parametrize(
    "name", [
        'WANCommonIFC1', 'WANDSLLinkC1', 'WANIPConn1'
    ])
def test_igd_description_services(name, igddesc_source):
    """
    Find services by name from nested devices (igddesc.xml)
    """
    d = Description(igddesc_source)
    service = d.services[name]
    assert service.name == name


@pytest.mark.parametrize(
    "name", [
        'DeviceInfo1', 'X_AVM-DE_Homeauto1', 'WLANConfiguration1',
        'WANCommonInterfaceConfig1', 'WANIPConnection1',
    ])
def test_tr64_description_services(name, tr64desc_source):
    """
    Find services by name from nested devices (tr64desc.xml)
    """
    d = Description(tr64desc_source)
    service = d.services[name]
    assert service.name == name


def test_system_version_igd(igddesc_source):
    d = Description(igddesc_source)
    assert d.system_version == None


def test_system_version_tr64(tr64desc_source):
    d = Description(tr64desc_source)
    assert d.system_version == '7.10'


def test_system_buildnumber_tr64(tr64desc_source):
    d = Description(tr64desc_source)
    assert d.system_buildnumber == '67453'


def test_scpd_specversion(scpd_instance):
    assert scpd_instance.spec_version == '1.0'


def test_scpd_actionlist(scpd_instance):
    # 18 actions are defined by 'igdconnSCPD.xml':
    assert len(scpd_instance._actions) == 18


def test_scpd_actiondict(scpd_instance):
    # 18 actions are defined by 'igdconnSCPD.xml':
    assert len(scpd_instance.actions) == 18


@pytest.mark.parametrize(
    "name", [
        'SetConnectionType', 'ForceTermination', 'X_AVM_DE_GetIPv6DNSServer'
    ])
def test_scpd_action_names(name, scpd_instance):
    # find some action names
    actions = scpd_instance.actions
    print(actions)
    action = actions[name]
    assert action.name == name


@pytest.mark.parametrize(
    "action_name, argument_name, direction, relatedStateVariable", [
        ('GetStatusInfo', 'NewConnectionStatus', 'out', 'ConnectionStatus'),
        ('GetStatusInfo', 'NewLastConnectionError', 'out', 'LastConnectionError'),
        ('GetStatusInfo', 'NewUptime', 'out', 'Uptime')
    ])
def test_scpd_action_argument_names(
        action_name, argument_name, direction,
        relatedStateVariable, scpd_instance
    ):
    """
    Test action arguments
    """
    action = scpd_instance.actions[action_name]
    argument = action.arguments[argument_name]
    assert argument.name == argument_name
    assert argument.direction == direction
    assert argument.relatedStateVariable == relatedStateVariable


def test_scpd_service_state_variables(scpd_instance):
    # 30 stateVariables are defined by 'igdconnSCPD.xml':
    assert len(scpd_instance._state_variables) == 30


@pytest.mark.parametrize(
    "name, data_type, default_value, allowed_values_num", [
        ('LastConnectionError', 'string', 'ERROR_NONE', 23),
        ('AutoDisconnectTime', 'ui4', '0', 0),
    ])
def test_scpd_service_state_variables_by_name(
        name, data_type, default_value, allowed_values_num, scpd_instance
    ):
    sv = scpd_instance.state_variables[name]
    assert sv.name == name
    assert sv.dataType == data_type
    assert sv.defaultValue == default_value
    assert len(sv.allowed_values) == allowed_values_num


def test_scpd_statevariable_allowed_value(scpd_instance):
    sv = scpd_instance.state_variables['LastConnectionError']
    assert 'ERROR_NO_CARRIER' in sv.allowed_values


def test_scpd_statevariable_allowed_range(scpd_instance):
    sv = scpd_instance.state_variables['Uptime']
    allowed_range = sv.allowedValueRange
    assert allowed_range.minimum == '0'
    assert allowed_range.maximum == '4294967295'
    assert allowed_range.step == '1'
