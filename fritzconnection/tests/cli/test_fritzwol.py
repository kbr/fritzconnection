import pytest

from fritzconnection.cli.fritzwol import WakeOnLan, WakeOnLanException
from unittest.mock import Mock

from fritzconnection.core.exceptions import FritzConnectionException


@pytest.fixture
def fritz_connection():
    return Mock()


@pytest.fixture
def fritz_hosts():
    mock = Mock()
    mock.get_hosts_info.return_value = [{'name': 'someHost',
                                         'mac': '00:00:00:00:00:00'}]
    return mock


def test_wol_is_invoked(fritz_connection, fritz_hosts):
    WakeOnLan(fritz_connection, fritz_hosts).wakeup("someHost")
    fritz_hosts.get_hosts_info.assert_called_once()
    fritz_connection.call_action.assert_called_once()


def test_host_not_found(fritz_connection, fritz_hosts):
    with pytest.raises(WakeOnLanException):
        WakeOnLan(fritz_connection, fritz_hosts).wakeup("unknownHost")

    fritz_connection.assert_not_called()


def test_call_action_causes_exception(fritz_connection, fritz_hosts):
    fritz_connection.call_action.side_effect = FritzConnectionException

    with pytest.raises(WakeOnLanException):
        WakeOnLan(fritz_connection, fritz_hosts).wakeup("somehost")

    fritz_hosts.get_hosts_info.assert_called_once()
