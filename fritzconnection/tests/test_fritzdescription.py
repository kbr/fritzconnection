import pathlib

import pytest

from fritzconnection.core.fritzdescription import FritzDescription
from fritzconnection.core.fritzdescription import FRITZ_IGD_DESC_FILE
from fritzconnection.core.fritzdescription import FRITZ_TR64_DESC_FILE


THIS_DIRECTORY = pathlib.Path(__file__).parent.resolve()
DESCRIPTION_FILES_DIR = THIS_DIRECTORY / "description_files"
TEST_MODEL_NAME = "FRITZ!Box 7590"
TEST_OS_VERSION = "8.02"
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


def test_get_cache_path():
    fd = FritzDescription(
        ip_address="192.168.178.1",
        cache_directory=DESCRIPTION_FILES_DIR
    )
    expected_path = DESCRIPTION_FILES_DIR / "192_168_178_1.cache"
    path = fd._get_cache_path(create_cache_dir=False)
    assert path == expected_path


def test_load_cache_nonexisting():
    fd = FritzDescription(
        ip_address="192.168.178.1",
        cache_directory=DESCRIPTION_FILES_DIR
    )
    result = fd.load_cache()
    assert result is False


def test_cache():
    igd_file = DESCRIPTION_FILES_DIR / "igddesc.xml"
    tr64_file = DESCRIPTION_FILES_DIR / "tr64desc.xml"
    boxinfo_file = DESCRIPTION_FILES_DIR / "jason_boxinfo.xml"

    fd = FritzDescription(
        ip_address="192.168.178.1",
        cache_directory=DESCRIPTION_FILES_DIR
    )
    fd.load_descriptions_from_source(igd_file, tr64_file)

    # check cache-file creation:
    expected_path = DESCRIPTION_FILES_DIR / "192_168_178_1.cache"
    assert expected_path.exists() is False
    fd.store_cache()
    assert expected_path.exists() is True
    try:
        # make a second instance, but load descriptions from the cache-file
        # both instances should have the same descriptions
        fd2 = FritzDescription(
            ip_address="192.168.178.1",
            cache_directory=DESCRIPTION_FILES_DIR
        )
        result = fd2.load_cache()
        assert result is True
        assert fd.check_cache(source=boxinfo_file) is True
        assert fd == fd2
    finally:
        # clean up:
        expected_path.unlink()
        assert expected_path.exists() is False


@pytest.mark.parametrize(
    "source, expected_result", [
        ("jason_boxinfo.xml", True),
        ("jason_wrong_boxinfo.xml", False),
    ]
)
def test_check_cache(source, expected_result):
    igd_file = DESCRIPTION_FILES_DIR / "igddesc.xml"
    tr64_file = DESCRIPTION_FILES_DIR / "tr64desc.xml"
    boxinfo_file = DESCRIPTION_FILES_DIR / source

    fd = FritzDescription(
        ip_address="192.168.178.1",
        cache_directory=DESCRIPTION_FILES_DIR
    )
    fd.load_descriptions_from_source(igd_file, tr64_file)
    assert fd.check_cache(source=boxinfo_file) is expected_result
