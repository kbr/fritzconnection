"""
Tests for parsing the device description files like

    igddesc.xml
    tr64desc.xml

"""

from io import StringIO
from pathlib import Path

import pytest

from lxml import etree
#import xml.etree.ElementTree as etree  # like lxml
import pytest


IGDDESC_FILE = Path(__file__).parent / 'xml' / 'igddesc.xml'


from ..fritzconnection.fritzconnection import (
    SpecVersion,
    Service,
    ServiceList,
    Device,
    DeviceList,
    Description,
)


def parse_xml(source):
    tree = etree.parse(StringIO(source))
    root = tree.getroot()
    return root


# --------------------------------------------------------
# test Description nodes
# --------------------------------------------------------

# Node: SpecVersion -----------------------------
spec_version_inp = parse_xml("""
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
""")

def test_SpecVersion_attributes(root=spec_version_inp):
    """test for instance attributes:"""
    sv = SpecVersion(root)
    assert sv.major == '1'
    assert sv.minor == '0'

def test_SpecVersion_version(root=spec_version_inp):
    """test version attribute"""
    sv = SpecVersion(root)
    assert sv.version == '1.0'


# Node: Service ---------------------------------
service_inp = parse_xml("""
    <service>
        <serviceType>urn:schemas-upnp-org:service:WANIPConnection:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:WANIPConn1</serviceId>
        <controlURL>/igdupnp/control/WANIPConn1</controlURL>
        <eventSubURL>/igdupnp/control/WANIPConn1</eventSubURL>
        <SCPDURL>/igdconnSCPD.xml</SCPDURL>
    </service>
""")

def test_Service_attributes(root=service_inp):
    """test for instance attributes:"""
    s = Service(root)
    assert s.serviceType == 'urn:schemas-upnp-org:service:WANIPConnection:1'
    assert s.serviceId == 'urn:upnp-org:serviceId:WANIPConn1'
    assert s.controlURL == '/igdupnp/control/WANIPConn1'
    assert s.eventSubURL == '/igdupnp/control/WANIPConn1'
    assert s.SCPDURL == '/igdconnSCPD.xml'

def test_Service_name(root=service_inp):
    """the service name is the last part of the serviceId"""
    s = Service(root)
    assert s.name == 'WANIPConn1'


# Node: ServiceList -----------------------------
service_list_inp = parse_xml("""
    <serviceList>
        <service>
            <serviceType>urn:schemas-upnp-org:service:WANDSLLinkConfig:1</serviceType>
            <serviceId>urn:upnp-org:serviceId:WANDSLLinkC1</serviceId>
            <controlURL>/igdupnp/control/WANDSLLinkC1</controlURL>
            <eventSubURL>/igdupnp/control/WANDSLLinkC1</eventSubURL>
            <SCPDURL>/igddslSCPD.xml</SCPDURL>
        </service>
        <service>
            <serviceType>urn:schemas-upnp-org:service:WANIPConnection:1</serviceType>
            <serviceId>urn:upnp-org:serviceId:WANIPConn1</serviceId>
            <controlURL>/igdupnp/control/WANIPConn1</controlURL>
            <eventSubURL>/igdupnp/control/WANIPConn1</eventSubURL>
            <SCPDURL>/igdconnSCPD.xml</SCPDURL>
        </service>
        <service>
            <serviceType>urn:schemas-upnp-org:service:WANIPv6FirewallControl:1</serviceType>
            <serviceId>urn:upnp-org:serviceId:WANIPv6Firewall1</serviceId>
            <controlURL>/igd2upnp/control/WANIPv6Firewall1</controlURL>
            <eventSubURL>/igd2upnp/control/WANIPv6Firewall1</eventSubURL>
            <SCPDURL>/igd2ipv6fwcSCPD.xml</SCPDURL>
        </service>
    </serviceList>
""")

def test_ServiceList_attributes(root=service_list_inp):
    """test for instance attributes:"""
    s = ServiceList(root)
    assert isinstance(s.service, list) is True

def test_ServiceList_service_len(root=service_list_inp):
    """test whether all services are listed."""
    s = ServiceList(root)
    assert len(s.service) == 3

def test_ServiceList_is_service_iterator(root=service_list_inp):
    """ServiceList behaves like a list of Services."""
    s = ServiceList(root)
    for n, service in enumerate(s, start=1):
        pass
    assert len(s.service) == n


# Node: Device ----------------------------------
device_inp = parse_xml("""
    <device>
        <deviceType>urn:schemas-upnp-org:device:InternetGatewayDevice:1</deviceType>
        <friendlyName>FRITZ!Box 7590</friendlyName>
        <manufacturer>AVM Berlin</manufacturer>
        <manufacturerURL>http://www.avm.de</manufacturerURL>
        <modelDescription>FRITZ!Box 7590</modelDescription>
        <modelName>FRITZ!Box 7590</modelName>
        <modelNumber>avm</modelNumber>
        <modelURL>http://www.avm.de</modelURL>
        <UDN>uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0</UDN>
        <iconList>
            <icon>
                <mimetype>image/gif</mimetype>
                <width>118</width>
                <height>119</height>
                <depth>8</depth>
                <url>/ligd.gif</url>
            </icon>
        </iconList>
    </device>
""")

@pytest.mark.parametrize(
    "root, name, value", [
        (device_inp, 'deviceType', 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'),
        (device_inp, 'friendlyName', 'FRITZ!Box 7590'),
        (device_inp, 'manufacturer', 'AVM Berlin'),
        (device_inp, 'manufacturerURL', 'http://www.avm.de'),
        (device_inp, 'modelDescription', 'FRITZ!Box 7590'),
        (device_inp, 'modelName', 'FRITZ!Box 7590'),
        (device_inp, 'modelNumber', 'avm'),
        (device_inp, 'modelURL', 'http://www.avm.de'),
        (device_inp, 'UDN', 'uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0'),
        (device_inp, 'iconList', ''),
    ]
)
def test_Device_attributes(root, name, value):
    """test for instance attributes:"""
    d = Device(root)
    assert getattr(d, name) == value

@pytest.mark.parametrize(
    "root, name, value", [
        (device_inp, 'deviceType', True),
        (device_inp, 'iconList', True),
        (device_inp, 'icon', False),
        (device_inp, 'mimetype', False),
    ]
)
def test_Device_skip_nested_attributes(root, name, value):
    """test for instance attributes:"""
    d = Device(root)
    assert hasattr(d, name) is value


# Node: Device plus ServiceList -----------------
device_services_inp = parse_xml("""
<device>
    <deviceType>urn:schemas-upnp-org:device:InternetGatewayDevice:1</deviceType>
    <friendlyName>FRITZ!Box 7590</friendlyName>
    <manufacturer>AVM Berlin</manufacturer>
    <manufacturerURL>http://www.avm.de</manufacturerURL>
    <modelDescription>FRITZ!Box 7590</modelDescription>
    <modelName>FRITZ!Box 7590</modelName>
    <modelNumber>avm</modelNumber>
    <modelURL>http://www.avm.de</modelURL>
    <UDN>uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0</UDN>
    <iconList>
        <icon>
            <mimetype>image/gif</mimetype>
            <width>118</width>
            <height>119</height>
            <depth>8</depth>
            <url>/ligd.gif</url>
        </icon>
    </iconList>
    <serviceList>
        <service>
            <serviceType>urn:schemas-any-com:service:Any:1</serviceType>
            <serviceId>urn:any-com:serviceId:any1</serviceId>
            <controlURL>/igdupnp/control/any</controlURL>
            <eventSubURL>/igdupnp/control/any</eventSubURL>
            <SCPDURL>/any.xml</SCPDURL>
        </service>
    </serviceList>
</device>
""")

def test_Device_has_ServiceList(root=device_services_inp):
    """test for serviceList attribute in Device"""
    d = Device(root)
    assert hasattr(d, 'serviceList') is True

def test_Device_has_services(root=device_services_inp):
    """services is a property refering the ServiceList instance."""
    d = Device(root)
    assert isinstance(d.services, ServiceList) is True

def test_Device_ServiceList_has_entry(root=device_services_inp):
    """test for services attribute in Device"""
    d = Device(root)
    # serviceList has one entry
    assert len(d.services) == 1

def test_Device_ServiceList_has_Services(root=device_services_inp):
    """test for content of services"""
    d = Device(root)
    for item in d.services:
        assert isinstance(item, Service)


# Node: Device plus Device- and ServiceList -----
device_devices_services_inp = parse_xml("""
    <device>
        <deviceType>urn:schemas-upnp-org:device:InternetGatewayDevice:1</deviceType>
        <friendlyName>FRITZ!Box 7590</friendlyName>
        <manufacturer>AVM Berlin</manufacturer>
        <manufacturerURL>http://www.avm.de</manufacturerURL>
        <modelDescription>FRITZ!Box 7590</modelDescription>
        <modelName>FRITZ!Box 7590</modelName>
        <modelNumber>avm</modelNumber>
        <modelURL>http://www.avm.de</modelURL>
        <UDN>uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0</UDN>
        <iconList>
            <icon>
                <mimetype>image/gif</mimetype>
                <width>118</width>
                <height>119</height>
                <depth>8</depth>
                <url>/ligd.gif</url>
            </icon>
        </iconList>
        <serviceList>
            <service>
                <serviceType>urn:schemas-any-com:service:Any:1</serviceType>
                <serviceId>urn:any-com:serviceId:any1</serviceId>
                <controlURL>/igdupnp/control/any</controlURL>
                <eventSubURL>/igdupnp/control/any</eventSubURL>
                <SCPDURL>/any.xml</SCPDURL>
            </service>
        </serviceList>
        <deviceList>
            <device>
                <deviceType>urn:schemas-upnp-org:device:WANDevice:1</deviceType>
                <friendlyName>WANDevice - FRITZ!Box 7590</friendlyName>
                <manufacturer>AVM Berlin</manufacturer>
                <manufacturerURL>www.avm.de</manufacturerURL>
                <modelDescription>WANDevice - FRITZ!Box 7590</modelDescription>
                <modelName>WANDevice - FRITZ!Box 7590</modelName>
                <modelNumber>avm</modelNumber>
                <modelURL>www.avm.de</modelURL>
                <UDN>uuid:76802409-bccb-40e7-8e6b-989BCB2B93B0</UDN>
                <UPC>AVM IGD</UPC>
                <serviceList>
                    <service>
                        <serviceType>urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1</serviceType>
                        <serviceId>urn:upnp-org:serviceId:WANCommonIFC1</serviceId>
                        <controlURL>/igdupnp/control/WANCommonIFC1</controlURL>
                        <eventSubURL>/igdupnp/control/WANCommonIFC1</eventSubURL>
                        <SCPDURL>/igdicfgSCPD.xml</SCPDURL>
                    </service>
                </serviceList>
            </device>
        </deviceList>
    </device>
""")


def test_Device_has_DeviceList(root=device_devices_services_inp):
    """test for serviceList attribute in Device"""
    d = Device(root)
    assert hasattr(d, 'deviceList') is True

def test_Device_has_devices(root=device_devices_services_inp):
    """devices is a property refering the DeviceList instance."""
    d = Device(root)
    assert isinstance(d.devices, DeviceList) is True

def test_Device_DeviceList_has_entry(root=device_devices_services_inp):
    """test for devices attribute in Device"""
    d = Device(root)
    # deviceList has one entry
    assert len(d.devices) == 1

def test_Device_ServiceList_has_Services(root=device_devices_services_inp):
    """test for content of devices"""
    d = Device(root)
    for item in d.devices:
        assert isinstance(item, Device)


# Node: Description -----------------------------
with open(IGDDESC_FILE) as fobj:
    description_inp = parse_xml(fobj.read())

def test_description_has_namespace(root=description_inp):
    """check for knowledge of namespace"""
    d = Description(root)
    assert hasattr(d, 'namespace') is True

def test_description_namespace(root=description_inp):
    """check for knowledge of namespace"""
    d = Description(root)
    assert d.namespace == "urn:schemas-upnp-org:device-1-0"

def test_description_specification(root=description_inp):
    """check for knowledge of protocol specification"""
    d = Description(root)
    assert d.specification == '1.0'

def test_description_modelname(root=description_inp):
    """check for knowledge of protocol specification"""
    d = Description(root)
    assert d.modelname == 'FRITZ!Box 7590'

@pytest.mark.parametrize(
    "root, servicename", [
        (description_inp, 'any1'),
        (description_inp, 'WANCommonIFC1'),
        (description_inp, 'WANDSLLinkC1'),
        (description_inp, 'WANIPConn1'),
        (description_inp, 'WANIPv6Firewall1'),
    ]
)
def test_description_collect_services(root, servicename):
    """
    collects the services from all devices in a dictionary: servicenames
    are the keys, the service instances are the values.
    """
    d = Description(root)
    services = d.collect_services()
    assert services[servicename].name == servicename
