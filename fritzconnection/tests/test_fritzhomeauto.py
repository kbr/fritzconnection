
import json
import pathlib
import pytest

from ..lib.fritzhomeauto import HomeAutomationDevice


# take some real data from a switch
DEVICE_INFORMATION = {
    'NewAIN': '11657 0240192',
    'NewDeviceId': 16,
    'NewFunctionBitMask': 35712,
    'NewFirmwareVersion': '04.25',
    'NewManufacturer': 'AVM',
    'NewProductName': 'FRITZ!DECT 210',
    'NewDeviceName': 'FRITZ!DECT 210 #1',
    'NewPresent': 'CONNECTED',
    'NewMultimeterIsEnabled': 'ENABLED',
    'NewMultimeterIsValid': 'VALID',
    'NewMultimeterPower': 0,
    'NewMultimeterEnergy': 16659,
    'NewTemperatureIsEnabled': 'ENABLED',
    'NewTemperatureIsValid': 'VALID',
    'NewTemperatureCelsius': 195,
    'NewTemperatureOffset': 0,
    'NewSwitchIsEnabled': 'ENABLED',
    'NewSwitchIsValid': 'VALID',
    'NewSwitchState': 'OFF',
    'NewSwitchMode': 'AUTO',
    'NewSwitchLock': False,
    'NewHkrIsEnabled': 'DISABLED',
    'NewHkrIsValid': 'INVALID',
    'NewHkrIsTemperature': 0,
    'NewHkrSetVentilStatus': 'CLOSED',
    'NewHkrSetTemperature': 0,
    'NewHkrReduceVentilStatus': 'CLOSED',
    'NewHkrReduceTemperature': 0,
    'NewHkrComfortVentilStatus': 'CLOSED',
    'NewHkrComfortTemperature': 0
}

BASICDEVICESTATS_RESPONSE_FILENAME = "basicdevicestats_response.txt"


def test_homeautomation_device_properties():
    """
    Test whether a switch provides a property of a switch, but not other
    properties. A switch as 'FRITZ!DECT 210' is

        - an energy sensor
        - a temperature sensor
        - pluggable
        - and has a microphone

    """
    dp = HomeAutomationDevice(None, DEVICE_INFORMATION)
    assert dp.is_han_fun_unit is False
    assert dp.is_bulb is False
    assert dp.is_alarm_sensor is False
    assert dp.is_avm_button is False
    assert dp.is_radiator_control is False
    assert dp.is_energy_sensor is True
    assert dp.is_temperature_sensor is True
    assert dp.is_pluggable is True
    assert dp.is_avm_dect_repeater is False
    assert dp.is_microphone is True
    assert dp.is_switchable is True
    assert dp.is_adjustable is False
    assert dp.is_color_bulb is False
    assert dp.is_blind is False
    assert dp.is_humidity_sensor is False


def test_homeautomation_device_properties_with_ain():
    """
    Provides an additional ain to the one already in DEVICE_INFORMATION.
    The one in DEVICE_INFORMATION should be preserved.
    """
    original_ain = DEVICE_INFORMATION['NewAIN']
    other_ain = '00000 1111111'
    dp = HomeAutomationDevice(None, DEVICE_INFORMATION , identifier=other_ain)
    assert dp.identifier == original_ain


def test_homeautomation_device_properties_without_ain():
    """
    Provides an ain because the entry in DEVICE_INFORMATION is missing.
    """
    # don't modify the constant DEVICE_INFORMATION
    device_information = {
        k: v for k, v in DEVICE_INFORMATION.items() if k != "NewAIN"
    }
    other_ain = '00000 1111111'
    dp = HomeAutomationDevice(None, device_information , identifier=other_ain)
    assert dp.identifier == other_ain


def test_extract_basicdevicestats_response(datadir):
    """
    Inject some data from a real device with an energy sensor.
    """
    expected_counts = {
        "temperature": 96,
        "voltage": 360,
        "power": 360,
        "energy": 12
    }
    file = datadir / BASICDEVICESTATS_RESPONSE_FILENAME
    text = file.read_text(encoding="utf-8")
    response = {
        "content-type": "text/xml",
        "encoding": "charset=utf-8",
        "content": text.strip()
    }
    result = HomeAutomationDevice.extract_basicdevicestats_response(response)
    for key in ("temperature", "voltage", "power", "energy"):
        assert key in result
        count = result[key]['count']
        assert count == expected_counts[key]
        assert count == len(result[key]['data'])
