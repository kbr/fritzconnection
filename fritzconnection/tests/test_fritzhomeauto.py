
import pytest

from ..lib.fritzhomeauto import DeviceProperties



def test_device_propertied():
    function_bit_map = 35712
    dp = DeviceProperties(function_bit_map)
    assert dp.is_radiator_control is False
    assert dp.is_switchable is True
    assert dp.is_humidity_sensor is False
