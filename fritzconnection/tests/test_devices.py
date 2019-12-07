from io import StringIO
from pathlib import Path
import os

import pytest
from xml.etree import ElementTree as etree

from ..core.devices import DeviceManager

@pytest.mark.parametrize("filename", [
    "igddesc.xml",
    "tr64desc.xml",
]
                         )
def test_DeviceManager_load_descriptions(device_manager, datadir, filename):
    """test loading of two description files."""
    os.chdir(datadir)
    device_manager.add_description(filename)
    assert device_manager.modelname == 'FRITZ!Box 7590'


@pytest.fixture()
def device_manager(datadir):
    os.chdir(datadir)
    manager = DeviceManager()
    manager.add_description('igddesc.xml')
    manager.add_description('tr64desc.xml')
    return manager


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
