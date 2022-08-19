import pytest

from ..lib.fritztools import (
    ArgumentNamespace,
    byte_formatter,
    format_num,
)


@pytest.mark.parametrize(
    "value, result, dimension", [
        (1, 1.0, 'B'),
        (123, 123.0, 'B'),
        (1230, 1.230, 'KB'),
        (12345, 12.345, 'KB'),
        (242981246, 242.981246, 'MB'),
        (24298124612, 24.298124612, 'GB'),
        (2429812461200, 2.4298124612, 'TB'),
        (42e3, 42.0, 'KB'),
        (42e6, 42.0, 'MB'),
        (42e9, 42.0, 'GB'),
        (42e12, 42.0, 'TB'),
        (42e15, 42.0, 'PB'),
        (42e18, 42000.0, 'PB'),
        (1.0, 1.0, 'B'),
        (0.1, 0, 'B'),
        (0.01, 0, 'B'),
        (0.001, 0, 'B'),
        (0, 0, 'B'),
        (-10, 10, 'B'),
    ]
)
def test_byte_formatter(value, result, dimension):
    num, dim = byte_formatter(value)
    assert num == result
    assert dim == dimension


@pytest.mark.parametrize(
    "num, formated_num", [
        (300, '300.0 B'),
        (2000, '2.0 KB'),
        (3500, '3.5 KB'),
        (32500, '32.5 KB'),
        (242911246, '242.9 MB'),
        (242981246, '243.0 MB'),
        (45e6, '45.0 MB'),
        (45e9, '45.0 GB'),
        (45e12, '45.0 TB'),
        (45e15, '45.0 PB'),
        (45e18, '45000.0 PB'),
    ]
)
def test_format_num(num, formated_num):
    assert formated_num == format_num(num)


def test_format_num_bits():
    result = format_num(1234, unit='bits')
    assert result == '1.2 KBit'


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
    info = ArgumentNamespace(source, mapping)
    assert info.serial_number == '989BCB2B93B0'
    assert info['model_name'] == 'FRITZ!Box 7590'


@pytest.mark.parametrize(
    "name, expected_result", [
        ("description", "description"),
        ("Description", "description"),
        ("ModelName", "model_name"),
        ("NewUpTime", "new_up_time"),
        ("new_up_time", "new_up_time"),
    ]
)
def test_argument_namespace_rewrite(name, expected_result):
    result = ArgumentNamespace.rewrite_argument(name, suppress_new=False)
    assert result == expected_result


@pytest.mark.parametrize(
    "name, expected_result", [
        ("NewUpTime", "up_time"),
        ("UpTime", "up_time"),
        ("upTime", "up_time"),
        ("up_time", "up_time"),
        ("uptime", "uptime"),
        ("newuptime", "newuptime"),
        ("Newuptime", "newuptime"),
        ("New_uptime", "uptime"),
    ]
)
def test_argument_namespace_rewrite_no_new(name, expected_result):
    result = ArgumentNamespace.rewrite_argument(name)
    assert result == expected_result


@pytest.fixture()
def avm_source():
    source = {
        'NewModelName': 'FRITZ!Box 7590',
        'NewDescription': 'FRITZ!Box 7590 154.07.29',
        'NewProductClass': 'AVMFB7590',
        'NewSerialNumber': '989BCB2B93B0',
    }
    return source


def test_argument_namespace_no_mapping(avm_source):
    """
    In case of a missing mapping, all values from source should get
    transfered to the ArgumentNamespace and the key should get converted
    to snake_case.
    """
    info = ArgumentNamespace(avm_source)
    assert info.model_name == 'FRITZ!Box 7590'
    assert info['model_name'] == 'FRITZ!Box 7590'


def test_argument_namespace_no_mapping_no_suppress(avm_source):
    """
    In case of a missing mapping, all values from source should get
    transfered to the ArgumentNamespace and the key should get converted
    to snake_case.
    """
    info = ArgumentNamespace(avm_source, suppress_new=False)
    assert info.new_serial_number == '989BCB2B93B0'
    assert info['new_serial_number'] == '989BCB2B93B0'
    assert info.new_model_name == 'FRITZ!Box 7590'
    assert info['new_model_name'] == 'FRITZ!Box 7590'


def test_argument_namespace_has_len(avm_source):
    info = ArgumentNamespace(avm_source)
    assert len(info) == len(avm_source)


def test_argument_namespace_assignment(avm_source):
    info = ArgumentNamespace(avm_source)
    info.new_value = 42
    assert info.new_value == 42
    assert len(info) == len(avm_source) + 1
    info["minus"] = -3
    assert info["minus"] == -3
    assert info.minus == -3
    assert len(info) == len(avm_source) + 2
