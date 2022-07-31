import os
import pytest

from ..core.utils import get_xml_root
from ..core.processor import HostStorage


@pytest.fixture()
def devicehostlist_source(datadir):
    os.chdir(datadir)
    return get_xml_root('devicehostlist.xml')


@pytest.mark.parametrize(
    "idx, attribute, expected_value", [
        (1, "Index", 1),
        (1, "IPAddress", "192.168.178.54"),
        (1, "MACAddress", "F8:4D:89:7C:0A:32"),
        (1, "Active", True),
        (1, "HostName", "MacBook"),
        (1, "InterfaceType", "802.11"),
        (1, "X_AVM-DE_Port", 0),
        (1, "X_AVM-DE_Speed", 866),
        (1, "X_AVM-DE_UpdateAvailable", False),
        (1, "X_AVM-DE_UpdateSuccessful", "unknown"),
        (1, "X_AVM-DE_InfoURL", None),
        (1, "X_AVM-DE_Model", None),
        (1, "X_AVM-DE_URL", None),
        (1, "X_AVM-DE_Guest", False),
        (1, "X_AVM-DE_VPN", False),
        (1, "X_AVM-DE_WANAccess", "granted"),
        (1, "X_AVM-DE_Disallow", False),

        (2, "Index", 2),
        (2, "IPAddress", "192.168.178.34"),
        (2, "MACAddress", "C2:39:6F:FB:A3:E8"),
        (2, "Active", True),
        (2, "HostName", "fritz.repeater"),
        (2, "InterfaceType", "Ethernet"),
        (2, "X_AVM-DE_Port", 3),
        (2, "X_AVM-DE_Speed", 100),
        (2, "X_AVM-DE_UpdateAvailable", False),
        (2, "X_AVM-DE_UpdateSuccessful", "succeeded"),
        (2, "X_AVM-DE_InfoURL", None),
        (2, "X_AVM-DE_Model", "FRITZ!Repeater 1200"),
        (2, "X_AVM-DE_URL", "http://192.168.178.34"),
        (2, "X_AVM-DE_Guest", False),
        (2, "X_AVM-DE_VPN", False),
        (2, "X_AVM-DE_WANAccess", "granted"),
        (2, "X_AVM-DE_Disallow", False),

        (3, "Index", 3),
        (3, "IPAddress", "192.168.178.49"),
        (3, "MACAddress", "B8:27:EB:D1:DC:06"),
        (3, "Active", True),
        (3, "HostName", "raspberrypi"),
        (3, "InterfaceType", "Ethernet"),
        (3, "X_AVM-DE_Port", 1),
        (3, "X_AVM-DE_Speed", 1000),
        (3, "X_AVM-DE_UpdateAvailable", False),
        (3, "X_AVM-DE_UpdateSuccessful", "unknown"),
        (3, "X_AVM-DE_InfoURL", None),
        (3, "X_AVM-DE_Model", None),
        (3, "X_AVM-DE_URL", None),
        (3, "X_AVM-DE_Guest", False),
        (3, "X_AVM-DE_VPN", False),
        (3, "X_AVM-DE_WANAccess", "granted"),
        (3, "X_AVM-DE_Disallow", False),

        (4, "Index", 4),
        (4, "IPAddress", "192.168.178.32"),
        (4, "MACAddress", "B4:CD:27:37:78:E4"),
        (4, "Active", False),
        (4, "HostName", "someones-HUAWEI"),
        (4, "InterfaceType", "802.11"),
        (4, "X_AVM-DE_Port", 0),
        (4, "X_AVM-DE_Speed", 0),
        (4, "X_AVM-DE_UpdateAvailable", False),
        (4, "X_AVM-DE_UpdateSuccessful", "unknown"),
        (4, "X_AVM-DE_InfoURL", None),
        (4, "X_AVM-DE_Model", None),
        (4, "X_AVM-DE_URL", None),
        (4, "X_AVM-DE_Guest", False),
        (4, "X_AVM-DE_VPN", False),
        (4, "X_AVM-DE_WANAccess", "granted"),
        (4, "X_AVM-DE_Disallow", False),
    ])
def test_readhostlist(idx, attribute, expected_value, devicehostlist_source):
    """
    Check for node-extraction and type conversion.
    """
    storage = HostStorage(devicehostlist_source)
    attrs = storage.hosts_attributes[idx-1]  # list is sorted but host-index is 1 based
    assert attrs[attribute] == expected_value
