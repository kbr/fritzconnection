import json
import os
from io import StringIO
from pathlib import Path

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


@pytest.fixture()
def device_manager_from_data(datadir):
    device_manager = DeviceManager()
    os.chdir(datadir)
    with open("description.json") as fobj:
        data = json.load(fobj)
    device_manager.deserialize(data)
    return device_manager


def test_DeviceManager_load_json_check_descriptions(device_manager_from_data):
    """
    test build up of a DeviceManager from json data.
    """
    dm = device_manager_from_data
    assert len(dm.descriptions) == 2  # based on the test-data


def test_DeviceManager_load_json_check_services_01(device_manager_from_data):
    """
    check for loaded services after calling .scan()
    """
    dm = device_manager_from_data
    assert dm.services == {}  # still empty
    # run scan() should fill the services:
    dm.scan()
    assert dm.services != {}


def test_DeviceManager_load_json_check_services_02(device_manager_from_data):
    """
    check for matching services after calling .scan()
    """
    dm = device_manager_from_data
    dm.scan()
    # "description_service_names.txt" corresponds to "description.json"
    with open("description_service_names.txt") as fobj:
        service_names = list(map(str.strip, fobj))
    known_services = dm.services.keys()
    # check for same number of services:
    assert len(known_services) == len(service_names)
    # check for same service names:
    for name in service_names:
        assert name in known_services


def test_DeviceManager_load_json_check_actions(device_manager_from_data):
    """
    Simple test whether actions are available from the services (which
    in turn get the actions from the _scpd attribute).
    """
    dm = device_manager_from_data
    dm.scan()
    for service in dm.services.values():
        assert service.actions is not None
