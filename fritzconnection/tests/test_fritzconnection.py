
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

