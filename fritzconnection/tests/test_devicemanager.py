from io import StringIO
from pathlib import Path

import pytest
from xml.etree import ElementTree as etree

from ..core.devices import DeviceManager


IGDDESC_FILE = Path(__file__).parent/'xml'/'igddesc.xml'
TR64DESC_FILE = Path(__file__).parent/'xml'/'tr64desc.xml'


def parse_xml(source):
    tree = etree.parse(StringIO(source))
    root = tree.getroot()
    return root


@pytest.fixture(scope="module")
def device_manager():
    manager = DeviceManager()
    with open(IGDDESC_FILE) as f1, open(TR64DESC_FILE) as f2:
        manager.add_description(f1)
        manager.add_description(f2)
    return manager


def test_DeviceManager_load_descriptions(device_manager):
    """test loading of two description files."""
    assert len(device_manager.descriptions) == 2


def test_DeviceManager_modelname(device_manager):
    """test loading of two description files."""
    assert device_manager.modelname == 'FRITZ!Box 7590'


@pytest.mark.parametrize(
    "name", ['WANIPConn1', 'DeviceConfig1', 'WLANConfiguration1']
)
def test_DeviceManager_get_service(name, device_manager):
    """
    test services dict of the DeviceManager. Should find nested services
    (from sub devices) and from different files.
    """
    device_manager.scan()
    # should not raise a KeyError
    service = device_manager.services[name]
    assert service.name == name



