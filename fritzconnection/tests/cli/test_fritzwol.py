from unittest.mock import Mock
from argparse import Namespace

from fritzconnection.cli.fritzwol import wake_host


def test_calls_wakeonlan_host_with_macaddress_directly():
    mac = 'C0:FF:EE:C0:FF:EE'
    fritz_host = Mock()

    wake_host(fritz_host, Namespace(field='mac', host=mac))
    fritz_host.get_generic_host_entry.assert_not_called()
    fritz_host.get_specific_host_entry_by_ip.assert_not_called()
    fritz_host.get_generic_host_entries.assert_not_called()

    fritz_host.wakeonlan_host.assert_called_with(mac)


def test_n_calls_generic_host_then_wakeonlan():
    mac = 'C0:FF:EE:C0:FF:EE'
    fritz_host = Mock()
    fritz_host.get_generic_host_entry.return_value = {'NewMACAddress': mac}

    wake_host(fritz_host, Namespace(field='n', host='1'))
    fritz_host.get_generic_host_entry.assert_called_with(0)
    fritz_host.get_specific_host_entry_by_ip.assert_not_called()
    fritz_host.get_generic_host_entries.assert_not_called()

    fritz_host.wakeonlan_host.assert_called_with(mac)


def test_ip_calls_specific_host_then_wakeonlan():
    mac = 'C0:FF:EE:C0:FF:EE'
    fritz_host = Mock()
    fritz_host.get_specific_host_entry_by_ip.return_value = {'NewMACAddress': mac}

    wake_host(fritz_host, Namespace(field='ip', host='127.0.0.1'))
    fritz_host.get_generic_host_entry.assert_not_called()
    fritz_host.get_specific_host_entry_by_ip.assert_called_with('127.0.0.1')
    fritz_host.get_generic_host_entries.assert_not_called()

    fritz_host.wakeonlan_host.assert_called_with(mac)



def test_name_calls_generic_host_entries_then_wakeonlan():
    mac = 'C0:FF:EE:C0:FF:EE'
    fritz_host = Mock()
    fritz_host.get_generic_host_entries.return_value = [
        {'NewHostName': 'otherhost', 'NewMACAddress': '11:22:33:44:55:66'},
        {'NewHostName': 'thishost', 'NewMACAddress': mac}
    ]

    wake_host(fritz_host, Namespace(field='name', host='thishost'))
    fritz_host.get_generic_host_entry.assert_not_called()
    fritz_host.get_specific_host_entry_by_ip.assert_not_called()
    fritz_host.get_generic_host_entries.assert_called_once()

    fritz_host.wakeonlan_host.assert_called_with(mac)
