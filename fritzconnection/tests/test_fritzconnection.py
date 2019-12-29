
import pytest

from ..core.fritzconnection import (
    FritzConnection,
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
    "url, use_tls, expected", [
        ('192.168.178.1', False, 'http://192.168.178.1'),
        ('192.168.178.1', True, 'https://192.168.178.1'),
        ('http://192.168.178.1', False, 'http://192.168.178.1'),
        ('http://192.168.178.1', True, 'https://192.168.178.1'),
        ('https://192.168.178.1', False, 'http://192.168.178.1'),
        ('https://192.168.178.1', True, 'https://192.168.178.1'),
    ]
)
def test_set_protocol(url, use_tls, expected):
    result = FritzConnection.set_protocol(url, use_tls)
    assert result == expected
