import pathlib

# import pytest

from fritzconnection.core.fritzdescription import FritzDescription
from fritzconnection.core.fritzdescription import FRITZ_IGD_DESC_FILE
from fritzconnection.core.fritzdescription import FRITZ_TR64_DESC_FILE



# from fritzconnection.core.description import TR64Description
# from fritzconnection.core.description import UPnPInternetGatewayDescription
# from fritzconnection.core.utils import get_xml_root


THIS_DIRECTORY = pathlib.Path(__file__).parent.resolve()
DESCRIPTION_FILES_DIR = THIS_DIRECTORY / "description_files"
TEST_MODEL_NAME = "FRITZ!Box 7590"
TEST_OS_VERSION = "8.02"
#TEST_TOTAL_DEVICES = 7
TEST_TOTAL_SERVICES = 42


def test_fritzdescription_load_descriptions():

    igd_file = DESCRIPTION_FILES_DIR / "igddesc.xml"
    tr64_file = DESCRIPTION_FILES_DIR / "tr64desc.xml"
    fd = FritzDescription()
    fd.load_descriptions_from_source(igd_file, tr64_file)

    # the decive has some properties/attributes:
    assert fd.device_name == TEST_MODEL_NAME
    assert fd.system_version == TEST_OS_VERSION
    assert len(fd.services) == TEST_TOTAL_SERVICES

