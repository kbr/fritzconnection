
import pytest


from ..core.utils import ArgumentNamespace


def test_argument_namespace():
    source = {
        'NewManufacturerName': 'AVM',
        'NewManufacturerOUI': '00040E',
        'NewModelName': 'FRITZ!Box 7590',
        'NewDescription': 'FRITZ!Box 7590 154.07.29',
        'NewProductClass': 'AVMFB7590',
        'NewSerialNumber': '989BCB2B93B0',
        'NewSoftwareVersion': '154.07.29',
        'NewHardwareVersion': 'FRITZ!Box 7590',
        'NewSpecVersion': '1.0',
        'NewProvisioningCode': '000.044.004.000',
        'NewUpTime': 9516949,
        'NewDeviceLog': 'long string here ...'
    }
    mapping = {
        "serial_number": "NewSerialNumber",
        "model_name": "NewModelName",
    }
    info = ArgumentNamespace(mapping, source)
    assert info.serial_number == '989BCB2B93B0'
    assert info['model_name'] == 'FRITZ!Box 7590'
