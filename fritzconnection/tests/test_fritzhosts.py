import pytest

from ..lib.fritzhosts import (
    FritzHosts,
)


@pytest.fixture()
def mesh_topology_fixture():
    return {'schema_version': '1.9',
            'nodes': [{'uid': 'n-1',
                'device_name': 'fritz.box',
                'device_model': 'FRITZ!Box Model',
                'device_manufacturer': 'AVM',
                'device_firmware_version': '111.11.11',
                'device_mac_address': '11:11:11:11:11:11',
                'is_meshed': True,
                'mesh_role': 'master',
                'meshd_version': '2.25',
                'node_interfaces': [{'uid': 'ni-237',
                    'name': 'AP:2G:0',
                    'type': 'WLAN',
                    'mac_address': '12:12:12:12:12:12',
                    'blocking_state': 'UNKNOWN',
                    'node_links': []},
                   {'uid': 'ni-236',
                    'name': 'LANBridge',
                    'type': 'LAN',
                    'mac_address': '11:11:11:11:11:11',
                    'blocking_state': 'UNKNOWN',
                    'node_links': []}]
                }],
            }


def test_get_mesh_topology_info(mesh_topology_fixture):
    """
    Simple test of the topology_info function.
    """
    host = FritzHosts()
    result = host.get_mesh_topology_info(topology=mesh_topology_fixture)
    node = mesh_topology_fixture['nodes'][0]
    assert result[node['device_mac_address']] == (node['is_meshed'], node['mesh_role'])

    # Return empty result upon FritzActionError:
    empty_result = host.get_mesh_topology_info(topology=None)
    assert empty_result == {}