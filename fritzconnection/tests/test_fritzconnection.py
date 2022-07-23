from pathlib import Path
from types import SimpleNamespace

import pytest

from ..core.fritzconnection import (
    FritzConnection,
    FRITZ_CACHE_DIR,
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


@pytest.mark.parametrize(
    "address, port, cache_directory, expected_result", [
        ('192.168.178.1', 49000, 'some_path', Path("some_path") / '192_168_178_1_cache.pcl'),
        ('192.168.178.1', 49000, '', Path().home() / FRITZ_CACHE_DIR / '192_168_178_1_cache.pcl'),
        ('192.168.178.1', 49000, None, Path().home() / FRITZ_CACHE_DIR / '192_168_178_1_cache.pcl'),
        ('192.168.178.6', 49000, None, Path().home() / FRITZ_CACHE_DIR / '192_168_178_6_cache.pcl'),
        ('192.168.1.15', 49000, None, Path().home() / FRITZ_CACHE_DIR / '192_168_1_15_cache.pcl'),
        ('http://192.168.1.15', 49000, None, Path().home() / FRITZ_CACHE_DIR / '192_168_1_15_cache.pcl'),
        ('https://192.168.1.15', 49000, None, Path().home() / FRITZ_CACHE_DIR / '192_168_1_15_cache.pcl'),
    ]
)
def test__get_cache_path(address, port, cache_directory, expected_result):
    # port parameter intentionally unused
    mock = SimpleNamespace(address=address, port=port)
    result = FritzConnection._get_cache_path(mock, cache_directory)
    assert result == expected_result
