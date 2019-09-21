"""
Tests for the main Description node and the ServiceManager
"""

from pathlib import Path
import pytest
from ..core.fritzconnection import (
    ServiceManager,
    ServiceError,
)


IGDDESC_FILE = Path(__file__).parent / 'xml' / 'igddesc.xml'
TR64DESC_FILE = Path(__file__).parent / 'xml' / 'tr64desc.xml'


@pytest.fixture(scope="module")
def service_manager():
    manager = ServiceManager()
    with open(IGDDESC_FILE) as f1, open(TR64DESC_FILE) as f2:
        manager.add_xml_description(f1)
        manager.add_xml_description(f2)
    return manager


def test_ServiceManager_load_descriptions(service_manager):
    """test loading od two description files."""
    assert len(service_manager.descriptions) == 2


def test_ServiceManager_modelname(service_manager):
    """test loading od two description files."""
    assert service_manager.modelname == 'FRITZ!Box 7590'


@pytest.mark.parametrize(
    "name, normalized_name", [
        ('WLANConfiguration', 'WLANConfiguration1'),
        ('WLANConfiguration1', 'WLANConfiguration1'),
        ('WLANConfiguration:1', 'WLANConfiguration1'),
        ('WLANConfiguration:2', 'WLANConfiguration2'),
        ('WLANConfiguration:12', 'WLANConfiguration12'),
    ]
)
def test_normalize_name(name, normalized_name, service_manager):
    """Convert different servicename forms to the internal used form."""
    assert service_manager.normalize_name(name) == normalized_name


ALL_SERVICENAMES = """
        any1
        WANCommonIFC1
        WANDSLLinkC1
        WANIPConn1
        WANIPv6Firewall1
        DeviceInfo1
        DeviceConfig1
        Layer3Forwarding1
        LANConfigSecurity1
        ManagementServer1
        Time1
        UserInterface1
        X_AVM-DE_Storage1
        X_AVM-DE_WebDAVClient1
        X_AVM-DE_UPnP1
        X_AVM-DE_Speedtest1
        X_AVM-DE_RemoteAccess1
        X_AVM-DE_MyFritz1
        X_VoIP1
        X_AVM-DE_OnTel1
        X_AVM-DE_Dect1
        X_AVM-DE_TAM1
        X_AVM-DE_AppSetup1
        X_AVM-DE_Homeauto1
        X_AVM-DE_Homeplug1
        X_AVM-DE_Filelinks1
        X_AVM-DE_Auth1
        WLANConfiguration1
        WLANConfiguration2
        WLANConfiguration3
        Hosts1
        LANEthernetInterfaceConfig1
        LANHostConfigManagement1
        WANCommonInterfaceConfig1
        WANDSLInterfaceConfig1
        WANDSLLinkConfig1
        WANEthernetLinkConfig1
        WANPPPConnection1
        WANIPConnection1
    """.split()

def test_for_all_servicenames(service_manager):
    """test for same length of services."""
    service_manager.scan()
    servicenames = list(service_manager.services.keys())
#     print(servicenames)
    assert len(servicenames) == len(ALL_SERVICENAMES)


@pytest.mark.parametrize(
    "name", ALL_SERVICENAMES
)
def test_for_finding_servicenames(name, service_manager):
    """test whether all services are available"""
    service_manager.scan()
    servicenames = list(service_manager.services.keys())
    # first check for key
    assert name in servicenames
    service = service_manager.services[name]
    # then check for same name
    assert name == service.name

def test_get_service_by_name_success(service_manager):
    """test valid service access"""
    name = 'WANIPConn1'
    service_manager.scan()
    # this should work:
    service = service_manager.get_service(name)
    # additional test:
    assert service.name == name

def test_get_service_by_name_failure(service_manager):
    """test valid service access"""
    name = 'weirdservicename'
    service_manager.scan()
    # this should not work: expect ServiceError
    with pytest.raises(ServiceError):
        service = service_manager.get_service(name)

