
import os
import pytest

from ..core.processor import (
    Description,
)
from ..core.utils import get_xml_root


@pytest.fixture()
def igddesc_source(datadir):
    os.chdir(datadir)
    return get_xml_root('igddesc.xml')


@pytest.mark.parametrize(
    "attribute, value", [
        ('spec_version', '1.0'),
        ('device_model_name', 'FRITZ!Box 7590'),
    ])
def test_igd_description_specversion(attribute, value, igddesc_source):
    d = Description(igddesc_source)
    assert d.spec_version == '1.0'


@pytest.mark.parametrize(
    "attribute, value", [
        ('deviceType', 'urn:schemas-upnp-org:device:InternetGatewayDevice:1'),
        ('friendlyName', 'FRITZ!Box 7590'),
        ('manufacturer', 'AVM Berlin'),
        ('manufacturerURL', 'http://www.avm.de'),
        ('modelDescription', 'FRITZ!Box 7590'),
        ('modelName', 'FRITZ!Box 7590'),
        ('modelNumber', 'avm'),
        ('modelURL', 'http://www.avm.de'),
        ('UDN', 'uuid:75802409-bccb-just-a-test-udn'),
    ])
def test_igd_device(attribute, value, igddesc_source):
    d = Description(igddesc_source)
    device = d.device
    assert getattr(device, attribute) == value


