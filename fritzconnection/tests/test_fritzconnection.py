
import pytest

from ..core.fritzconnection import (
    FritzConnection,
    boolean_convert,
)


@pytest.mark.parametrize(
    "name, expected", [
        ('WANIPConn', 'WANIPConn1'),
        ('WANIPConn1', 'WANIPConn1'),
        ('WANIPConn:1', 'WANIPConn1'),
        ('WANIPConn2', 'WANIPConn2'),
        ('WANIPConn:2', 'WANIPConn2'),
        ('WANIPConn21', 'WANIPConn21'),
        ('WANIPConn:21', 'WANIPConn21'),
    ]
)
def test_normalize_name(name, expected):
    result = FritzConnection.normalize_name(name)
    assert result == expected

@pytest.mark.parametrize(
    "value, expected_result", [
        ('0', False),
        ('1', True),
        ('2', True),
        ('x', 'x'),
        ('3.1', '3.1'),
    ]
)
def test_boolean_convert(value, expected_result):
    result = boolean_convert(value)
    assert result == expected_result
