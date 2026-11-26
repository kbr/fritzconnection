
import inspect
import os
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

import pytest

from ..core.devices import DeviceManager
from ..core.exceptions import FritzConnectionException
from ..core.processor import Service
from ..core.soaper import Soaper
from ..core.fritzconnection import (
    FritzConnection,
    FRITZ_CACHE_DIR,
    FRITZ_CACHE_FORMAT_JSON,
    FRITZ_CACHE_FORMAT_PICKLE,
    FRITZ_CACHE_JSON_SUFFIX,
    FRITZ_CACHE_PICKLE_SUFFIX,
    FRITZ_TCP_PORT,
    FRITZ_TLS_PORT,
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
        _ = FritzConnection._get_cache_path(mock, None, 'weird')


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


@pytest.fixture
def router_api():
    """Replaces the DeviceManager methods loading the api from the router."""
    with mock.patch.object(
        DeviceManager, "add_description"
    ) as add_description, mock.patch.object(
        DeviceManager, "scan"
    ) as scan, mock.patch.object(
        DeviceManager, "load_service_descriptions"
    ) as load_service_descriptions:
        yield SimpleNamespace(
            add_description=add_description,
            scan=scan,
            load_service_descriptions=load_service_descriptions,
        )


@pytest.mark.parametrize(
    "use_public_connection, expected_base, expected_prefix", [
        (False, "http://testaddress:1234", ""),
        (True, "https://testaddress:1234/tr064", "/tr064"),
    ]
)
def test_load_api_from_router_with_public_connection(
    router_api, use_public_connection, expected_base, expected_prefix
):
    """
    Accessing the box from the internet requires https and the path prefix
    "/tr064" for the description files and the scpd files.
    """
    connection = FritzConnection(
        address="testaddress",
        port=1234,
        use_public_connection=use_public_connection,
    )

    assert router_api.add_description.call_args_list == [
        mock.call(f"{expected_base}/igddesc.xml"),
        mock.call(f"{expected_base}/tr64desc.xml"),
    ]
    router_api.scan.assert_called_once()
    router_api.load_service_descriptions.assert_called_once_with(
        connection.address, 1234, path_prefix=expected_prefix
    )
    assert connection.path_prefix == expected_prefix
    assert connection.soaper.path_prefix == expected_prefix


def test_public_connection_implies_tls(router_api):
    """
    use_public_connection enforces https and the default tls-port
    in case no port is given.
    """
    connection = FritzConnection(
        address="example.myfritz.net", use_public_connection=True
    )
    assert connection.use_public_connection is True
    assert connection.address == "https://example.myfritz.net"
    assert connection.soaper.address == "https://example.myfritz.net"
    assert connection.port == FRITZ_TLS_PORT


def test_public_connection_default_is_off(router_api):
    """Without the flag the connection is unchanged."""
    connection = FritzConnection(address="192.168.178.1")
    assert connection.use_public_connection is False
    assert connection.path_prefix == ""
    assert connection.address == "http://192.168.178.1"
    assert connection.port == FRITZ_TCP_PORT


@pytest.mark.parametrize(
    "func, expected_leading_parameters", [
        (
            FritzConnection.__init__,
            ["self", "address", "port", "user", "password", "timeout",
             "use_tls", "use_cache", "verify_cache", "cache_directory",
             "cache_format", "pool_connections", "pool_maxsize",
             "redact_debug_log"],
        ),
        (
            Soaper.__init__,
            ["self", "address", "port", "user", "password", "timeout",
             "session", "redact_debug_log"],
        ),
        (Soaper.execute, ["self", "service", "action_name", "arguments"]),
        (
            Service.load_scpd,
            ["self", "address", "port", "timeout", "session"],
        ),
        (
            DeviceManager.load_service_descriptions,
            ["self", "address", "port"],
        ),
    ]
)
def test_public_connection_keeps_api_compatible(func, expected_leading_parameters):
    """
    The public connection support is optional: existing parameters keep
    their positions and every new parameter is appended with a default,
    so positional calls of existing code keep working.
    """
    parameters = list(inspect.signature(func).parameters.values())
    leading = parameters[:len(expected_leading_parameters)]
    assert [p.name for p in leading] == expected_leading_parameters
    for parameter in parameters[len(expected_leading_parameters):]:
        assert parameter.default is not inspect.Parameter.empty
