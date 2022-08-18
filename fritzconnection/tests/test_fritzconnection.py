
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from ..core.devices import DeviceManager
from ..core.exceptions import FritzConnectionException
from ..core.fritzconnection import (
    FritzConnection,
    FRITZ_CACHE_DIR,
    FRITZ_CACHE_FORMAT_JSON,
    FRITZ_CACHE_FORMAT_PICKLE,
    FRITZ_CACHE_JSON_SUFFIX,
    FRITZ_CACHE_PICKLE_SUFFIX,
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
    "address, port, cache_directory, cache_format, expected_result", [
        ('192.168.178.1', 49000, 'some_path', FRITZ_CACHE_FORMAT_PICKLE, Path("some_path") / f'192_168_178_1_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('192.168.178.1', 49000, '', FRITZ_CACHE_FORMAT_PICKLE, Path().home() / FRITZ_CACHE_DIR / f'192_168_178_1_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('192.168.178.1', 49000, None, FRITZ_CACHE_FORMAT_PICKLE, Path().home() / FRITZ_CACHE_DIR / f'192_168_178_1_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('192.168.178.6', 49000, None, FRITZ_CACHE_FORMAT_PICKLE, Path().home() / FRITZ_CACHE_DIR / f'192_168_178_6_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('192.168.1.15', 49000, None, FRITZ_CACHE_FORMAT_PICKLE, Path().home() / FRITZ_CACHE_DIR / f'192_168_1_15_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('http://192.168.1.15', 49000, None, FRITZ_CACHE_FORMAT_PICKLE, Path().home() / FRITZ_CACHE_DIR / f'192_168_1_15_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('https://192.168.1.15', 49000, None, FRITZ_CACHE_FORMAT_PICKLE, Path().home() / FRITZ_CACHE_DIR / f'192_168_1_15_cache.{FRITZ_CACHE_PICKLE_SUFFIX}'),
        ('192.168.178.1', 49000, 'some_path', FRITZ_CACHE_FORMAT_JSON, Path("some_path") / f'192_168_178_1_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
        ('192.168.178.1', 49000, '', FRITZ_CACHE_FORMAT_JSON, Path().home() / FRITZ_CACHE_DIR / f'192_168_178_1_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
        ('192.168.178.1', 49000, None, FRITZ_CACHE_FORMAT_JSON, Path().home() / FRITZ_CACHE_DIR / f'192_168_178_1_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
        ('192.168.178.6', 49000, None, FRITZ_CACHE_FORMAT_JSON, Path().home() / FRITZ_CACHE_DIR / f'192_168_178_6_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
        ('192.168.1.15', 49000, None, FRITZ_CACHE_FORMAT_JSON, Path().home() / FRITZ_CACHE_DIR / f'192_168_1_15_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
        ('http://192.168.1.15', 49000, None, FRITZ_CACHE_FORMAT_JSON, Path().home() / FRITZ_CACHE_DIR / f'192_168_1_15_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
        ('https://192.168.1.15', 49000, None, FRITZ_CACHE_FORMAT_JSON, Path().home() / FRITZ_CACHE_DIR / f'192_168_1_15_cache.{FRITZ_CACHE_JSON_SUFFIX}'),
    ]
)
def test_get_cache_path(address, port, cache_directory, cache_format, expected_result):
    # port parameter intentionally unused
    mock = SimpleNamespace(address=address, port=port)
    result = FritzConnection._get_cache_path(mock, cache_directory, cache_format)
    assert result == expected_result


def test_invalide_cache_format():
    mock = SimpleNamespace(address='192.168.178.1', port=49000)
    with pytest.raises(FritzConnectionException):
        result = FritzConnection._get_cache_path(mock, None, 'weird')


@pytest.mark.parametrize(
    "file_name, cache_format", [
        ("description.json", FRITZ_CACHE_FORMAT_JSON),
        ("description.pcl", FRITZ_CACHE_FORMAT_PICKLE),
    ]
)
def test_load_api_from_cache(file_name, cache_format, datadir):
    """
    Load the api from a cache file and check whether all
    known services are available.
    """
    os.chdir(datadir)
    mock = SimpleNamespace(device_manager=DeviceManager())
    FritzConnection._load_api_from_cache(mock, file_name, cache_format)
    with open("description_service_names.txt") as fobj:
        service_names = list(map(str.strip, fobj))
    known_services = mock.device_manager.services.keys()
    # check for same number of services:
    assert len(known_services) == len(service_names)
    # check for same service names:
    for name in service_names:
        assert name in known_services


@pytest.mark.parametrize(
    "file_name, cache_format", [
        ("description.json", FRITZ_CACHE_FORMAT_JSON),
        ("description.pcl", FRITZ_CACHE_FORMAT_PICKLE),
    ]
)
def test_write_api_to_cache(file_name, cache_format, datadir):
    """
    Tests writing the api data.

    For writing there must be some data first. If the test
    `test_load_api_from_cache` succeeds, the data can safely loaded to a
    FritzConnection mock object. The data are then exported to a file
    and loaded again to another FritzConnection mock object. Then the
    Decription objects are compared.
    """
    os.chdir(datadir)
    # 1. load the api data
    mock = SimpleNamespace(device_manager=DeviceManager())
    FritzConnection._load_api_from_cache(mock, file_name, cache_format)
    # 2. save the api data
    cache_filename = f"x_tmp_cache_{file_name}"
    cache_file = Path(cache_filename)

# TODO: (potentially)
# code for Python >= 3.8:
# cache_file.unlink(missing_ok=True)  # in case of artefacts
# code for Python < 3.8:
    try:
        cache_file.unlink()
    except FileNotFoundError:
        pass  # ignore

    FritzConnection._write_api_to_cache(mock, cache_filename, cache_format)
    assert cache_file.exists() is True
    # 3. read the api data to another mock
    other_mock = SimpleNamespace(device_manager=DeviceManager())
    FritzConnection._load_api_from_cache(other_mock, cache_filename, cache_format)
    # 4. the Descriptions are serializable and therefore comparable objects:
    for desc1, desc2 in zip(
        mock.device_manager.descriptions, other_mock.device_manager.descriptions
    ):
        assert desc1 == desc2
    # clean up
    cache_file.unlink()
    assert cache_file.exists() is False


