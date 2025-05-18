import pathlib

import pytest

from fritzconnection.core.description import AllowedValueList
from fritzconnection.core.description import Icon
from fritzconnection.core.description import IconList
from fritzconnection.core.description import UpnPInternetGatewayDescription
from fritzconnection.core.utils import get_xml_root


THIS_DIRECTORY = pathlib.Path(__file__).parent.resolve()
DESCRIPTION_FILES_DIR = THIS_DIRECTORY / "description_files"


def test_load_icon():
    """
    Check if the dataclass Icon is a Loader that can load its own attributes.
    """
    source = DESCRIPTION_FILES_DIR / "icon.xml"
    root = get_xml_root(source.as_posix())
    icon = Icon()
    icon.load(root)

    # check for all attributes:
    assert icon.mimetype == "image/gif"
    assert icon.width == "118"
    assert icon.height == "119"
    assert icon.depth == "8"
    assert icon.url == "/ligd.gif"

    # also tag-attributes should be there:
    assert len(icon.attrib) == 2
    assert icon.attrib["version"] == "1"
    assert icon.attrib["minor"] == "2"


def test_load_iconlist():
    """
    Load a node with subnodes.
    """
    source = DESCRIPTION_FILES_DIR / "iconlist.xml"
    root = get_xml_root(source.as_posix())
    iconlist = IconList()
    iconlist.load(root)

    # should be two nodes
    assert len(iconlist.list_items) == 2

    # and the nodes should be different nodes:
    assert iconlist.list_items[0].url != iconlist.list_items[1].url


def test_allowed_valuelist():
    """
    An allowedValueList has multiple subnodes `allowdValue` holding pure
    text. So the texts have to be stored in a list.
    """
    source = DESCRIPTION_FILES_DIR / "allowedvaluelist.xml"
    root = get_xml_root(source.as_posix())
    allowedvaluelist = AllowedValueList()
    allowedvaluelist.load(root)

    # should be three items
    assert len(allowedvaluelist.list_items) == 3

    # check the ordered content:
    items = ["1", "2", "3"]
    for item, expected in zip(allowedvaluelist.list_items, items):
        assert item == expected


def test_upnpinternetgatewaydescription_devices():
    """
    The router internally is a box of three upnp-devices:
    The router itself, a wan-device and a wan-connection-device
    """
    source = DESCRIPTION_FILES_DIR / "igddesc.xml"
    root = get_xml_root(source.as_posix())
    igd = UpnPInternetGatewayDescription()
    igd.load(root)

    # three devices should be known as well as the spec_version
    assert len(igd.devices) == 3
    assert igd.spec_version == "1.0"

