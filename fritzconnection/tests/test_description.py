import pathlib

# import pytest

from fritzconnection.core.description import AllowedValueList
from fritzconnection.core.description import Icon
from fritzconnection.core.description import IconList
from fritzconnection.core.description import SCPD
from fritzconnection.core.description import Service
from fritzconnection.core.description import TR64Description
from fritzconnection.core.description import UPnPInternetGatewayDescription
from fritzconnection.core.utils import get_xml_root


THIS_DIRECTORY = pathlib.Path(__file__).parent.resolve()
DESCRIPTION_FILES_DIR = THIS_DIRECTORY / "description_files"


def test_load_icon():
    """
    Check if a description dataclass can load its own attributes.
    This is tested with Icon as a placeholder for all classes
    of the same type (like i.e. Service or SpecVersion).
    """
    source = DESCRIPTION_FILES_DIR / "icon.xml"
    root = get_xml_root(source.as_posix())
    icon = Icon()
    icon.load(root)

    # check for all attributes:
    assert icon.mimetype == "image/gif"
    assert icon.width == "118"
    assert icon.height == "119"
    assert icon.depth == "8"
    assert icon.url == "/ligd.gif"

    # also tag-attributes should be there:
    assert len(icon.attrib) == 2
    assert icon.attrib["version"] == "1"
    assert icon.attrib["minor"] == "2"


def test_load_iconlist():
    """
    Test a node with a collection of subnodes in the attribute
    list_items. Here IconList is a placeholder for similar classes like
    ServiceList or DeviceList with the same structure.
    """
    source = DESCRIPTION_FILES_DIR / "iconlist.xml"
    root = get_xml_root(source.as_posix())
    iconlist = IconList()
    iconlist.load(root)

    # should be two nodes
    assert len(iconlist.list_items) == 2

    # and the nodes should be different nodes:
    assert iconlist.list_items[0].url != iconlist.list_items[1].url


def test_allowed_valuelist():
    """
    An allowedValueList has multiple subnodes `allowdValue` holding pure
    text. So the texts of the subnodes have to be stored in a list.
    """
    source = DESCRIPTION_FILES_DIR / "allowedvaluelist.xml"
    root = get_xml_root(source.as_posix())
    allowedvaluelist = AllowedValueList()
    allowedvaluelist.load(root)

    # should be three items
    assert len(allowedvaluelist.list_items) == 3

    # check the ordered content:
    items = ["1", "2", "3"]
    for item, expected in zip(allowedvaluelist.list_items, items):
        assert item == expected


def test_upnpinternetgatewaydescription_devices():
    """
    The router is a box of three nested upnp-devices:
    The router itself, which has a wan-device that has wan-connection-device.
    """
    source = DESCRIPTION_FILES_DIR / "igddesc.xml"
    root = get_xml_root(source.as_posix())
    igd = UPnPInternetGatewayDescription()
    igd.load(root)

    # there is a spec version:
    assert igd.spec_version == "1.0"

    # the three devices are hierarchically structured, but the
    # UPnPInternetGatewayDescription class stores them also in a mapping that
    # can be accessed as the property `devices` with the short device types as
    # key and the objects as values:
    igd_devices = igd.devices
    assert isinstance(igd_devices, dict) is True
    assert len(igd_devices) == 3

    # test the mapping for the devices:
    device_names = [
        "InternetGatewayDevice",
        "WANDevice",
        "WANConnectionDevice",
    ]
    for device_name in device_names:
        assert device_name in igd_devices

    # the three devices provide a total of five services. Every device knows
    # its own services but the UPnPInternetGatewayDescription class also
    # provides a mapping with the the service ids as key (which are unique)
    # and the corresponding service description as value:
    igd_services = igd.services
    assert isinstance(igd_services, dict) is True
    assert len(igd_services) == 5

    # test the mapping for the services:
    service_names = [
        "any1",
        "WANCommonIFC1",
        "WANDSLLinkC1",
        "WANIPConn1",
        "WANIPv6Firewall1"
    ]
    for service_name in service_names:
        assert service_name in igd_services


def test_tr64description_devices():
    source = DESCRIPTION_FILES_DIR / "tr64desc.xml"
    root = get_xml_root(source.as_posix())
    trd = TR64Description()
    trd.load(root)

    # there is a spec version:
    assert trd.spec_version == "1.0"

    # and also a system version that should get presented
    # as in the web-backend to reduce confusion:
    assert trd.system_version == "8.02"

    # TR064 provides four devices as for UPnP plus a LANDevice (which include
    # the WLAN)
    trd_devices = trd.devices
    assert isinstance(trd_devices, dict) is True
    assert len(trd_devices) == 4

    # test the mapping for the devices:
    device_names = [
        "InternetGatewayDevice",
        "WANDevice",
        "WANConnectionDevice",
        "LANDevice"
    ]
    for device_name in device_names:
        assert device_name in trd_devices

    # the TR064 services have the same structure like UPnP,
    # but the four devices have a total of 37 services.
    trd_services = trd.services
    assert isinstance(trd_services, dict) is True
    assert len(trd_services) == 37

    # test the mapping for the services:
    service_names = [
        "DeviceInfo1",
        "DeviceConfig1",
        "Layer3Forwarding1",
        "LANConfigSecurity1",
        "ManagementServer1",
        "Time1",
        "UserInterface1",
        "X_AVM-DE_Storage1",
        "X_AVM-DE_WebDAVClient1",
        "X_AVM-DE_UPnP1",
        "X_AVM-DE_Speedtest1",
        "X_AVM-DE_RemoteAccess1",
        "X_AVM-DE_MyFritz1",
        "X_VoIP1",
        "X_AVM-DE_OnTel1",
        "X_AVM-DE_Dect1",
        "X_AVM-DE_TAM1",
        "X_AVM-DE_AppSetup1",
        "X_AVM-DE_Homeauto1",
        "X_AVM-DE_Homeplug1",
        "X_AVM-DE_Filelinks1",
        "X_AVM-DE_Auth1",
        "X_AVM-DE_HostFilter1",
        "X_AVM-DE_USPController1",
        "WLANConfiguration1",
        "WLANConfiguration2",
        "WLANConfiguration3",
        "Hosts1",
        "LANEthernetInterfaceConfig1",
        "LANHostConfigManagement1",
        "WANCommonInterfaceConfig1",
        "WANDSLInterfaceConfig1",
        "X_AVM-DE_WANMobileConnection1",
        "WANDSLLinkConfig1",
        "WANEthernetLinkConfig1",
        "WANPPPConnection1",
        "WANIPConnection1",
    ]
    for service_name in service_names:
        assert service_name in trd_services


def test_service():
    source = DESCRIPTION_FILES_DIR / "service.xml"
    root = get_xml_root(source)
    service = Service()
    service.load(root)

    assert service.short_service_id == "DeviceConfig1"
    assert service.SCPDURL == "/deviceconfigSCPD.xml"
    assert service.scpd is None


def test_load_service_scpd():
    source = DESCRIPTION_FILES_DIR / "service.xml"
    root = get_xml_root(source)
    service = Service()
    service.load(root)

    # get the uri:
    assert service.SCPDURL == "/deviceconfigSCPD.xml"
    uri = DESCRIPTION_FILES_DIR / service.SCPDURL[1:]  # make a file-path

    # create the SCPD instance:
    assert service.scpd is None
    service.scpd = SCPD()
    root = get_xml_root(uri)
    service.scpd.load(root)

    # a service has a specVersion and a list of actions
    assert str(service.scpd.specVersion) == "1.0"
    assert len(service.scpd.actionList) == 14

    # for fast access the service must provide the actions as a mapping
    # `service.actions['action_name']`
    assert isinstance(service.actions, dict) is True
    assert len(service.actions) == 14
    # select an action and check for the arguments:
    action = service.actions["X_AVM-DE_GetConfigFile"]
    assert isinstance(action.arguments, dict) is True
    assert len(action.arguments) == 2
    assert "NewX_AVM-DE_Password" in action.arguments

    # the service must also provide a `state_variables` mapping
    assert isinstance(service.state_variables, dict) is True
    assert len(service.state_variables) == 12

