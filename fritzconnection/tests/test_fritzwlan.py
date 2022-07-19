"""
tests for qr-code creation
"""

import io
import os
import tempfile

import pytest

try:
    import cv2
    import segno.helpers
except ImportError:
    OPENCV_NOT_AVAILABLE = True
else:
    OPENCV_NOT_AVAILABLE = False

from fritzconnection.lib.fritzwlan import (
    get_beacon_security,
    get_wifi_qr_code,
)


@pytest.mark.skipif(OPENCV_NOT_AVAILABLE, reason="requires opencv")
def test_tools():
    """
    basic test whether opencv is able to read the output provided by segno.
    The tempfile is needed because opencv can not read from a file-like
    object but needs a path to the image-file.
    """
    ssid = 'xenon'
    password = 'the_strange_one'
    security = 'WPA'
    kind = 'png'
    # create qr-code and store it in a persistent temporary file
    stream = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{kind}')
    fname = stream.name
    qr_code = segno.helpers.make_wifi(
        ssid=ssid, password=password, security=security, hidden=False
    )
    qr_code.save(out=stream, kind=kind, scale=4)
    stream.close()
    assert os.path.exists(fname) is True

    # test qr-code reading
    expected_result = f'WIFI:T:{security};S:{ssid};P:{password};;'
    img = cv2.imread(fname)
    detector = cv2.QRCodeDetector()
    result, _, _ = detector.detectAndDecode(img)
    assert result == expected_result

    # remove the tempfile
    os.unlink(fname)
    assert os.path.exists(fname) is False


def write_stream_to_tempfile(stream, kind='png'):
    """
    Helper function to store a segno stream in a persistent tempfile.
    Takes the stream (BytesIO) and returns the filepath (as string).
    """
    fobj = tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix=f'.{kind}')
    fname = fobj.name
    fobj.write(stream.read())
    fobj.close()
    return fname


def get_content_from_qr_file(fname):
    """Helper function for qr-code reading."""
    img = cv2.imread(fname)
    detector = cv2.QRCodeDetector()
    result, _, _ = detector.detectAndDecode(img)
    return result


@pytest.mark.skipif(OPENCV_NOT_AVAILABLE, reason="requires opencv")
def test_helper_functions():
    ssid = 'xenon'
    password = 'another_strange_one'
    security = 'WPA'
    kind = 'png'
    stream = io.BytesIO()
    qr_code = segno.helpers.make_wifi(
        ssid=ssid, password=password, security=security, hidden=False
    )
    qr_code.save(out=stream, kind=kind, scale=4)
    stream.seek(0)
    # delegate stream to helper:
    fname = write_stream_to_tempfile(stream)
    # file must exist:
    assert os.path.exists(fname) is True
    # read qr-code:
    result = get_content_from_qr_file(fname)
    # check and clean up:
    expected_result = f'WIFI:T:{security};S:{ssid};P:{password};;'
    assert result == expected_result
    os.unlink(fname)
    assert os.path.exists(fname) is False


class WLANConfigMock:
    """
    Mocking class to provide the result of a
    WLANConfiguration.get_info() call, provide a get_password() method
    and a ssid attribute. All returned value must be part of the
    mock_data dictionary. The values in the dictionary are all strings.
    """

    def __init__(self, mock_data):
        self.mock_data = mock_data

    def get_info(self):
        return self.mock_data

    def get_password(self):
        # original from the action "GetSecurityKeys"
        return self.mock_data["NewKeyPassphrase"]

    @property
    def ssid(self):
        return self.mock_data["NewSSID"]


@pytest.mark.parametrize(
    "current_beacontype, security, expected_result", [
        ('11i', None, 'WPA'),
        ('11i', '', 'WPA'),
        ('11i', 'WPA3', 'WPA3'),
        ('WPAand11i', None, 'WPA'),
        ('11iandWPA3', None, 'WPA'),
        ('None', None, 'nopass'),
        ('OWETrans', None, 'nopass'),
    ]
)
def test_get_beacon_security(current_beacontype, security, expected_result):
    """
    Test for correct selection of "WPA" or "nopass" depending on the
    WLAN-settings.
    """
    mock_data = {
        'NewBeaconType': current_beacontype,
        'NewX_AVM-DE_PossibleBeaconTypes': 'None,11i,WPAand11i,11iandWPA3'
    }
    instance = WLANConfigMock(mock_data)
    result = get_beacon_security(instance, security)
    assert result == expected_result


@pytest.mark.skipif(OPENCV_NOT_AVAILABLE, reason="requires opencv")
@pytest.mark.parametrize(
    "current_beacontype, security, expected_security", [
        ('11i', None, 'WPA'),
        ('11i', '', 'WPA'),
        ('11i', 'WPA3', 'WPA3'),
        ('WPAand11i', None, 'WPA'),
        ('11iandWPA3', None, 'WPA'),
        ('None', None, 'nopass'),
        ('OWETrans', None, 'nopass'),
    ]
)
def test_get_wifi_qr_code(current_beacontype, security, expected_security):
    """
    Check for correct qr-code creation depending on the WLAN-settings.
    """
    ssid = "the_wlan_name"
    password = "the_password"
    expected_result = f"WIFI:T:{expected_security};S:{ssid};P:{password};;"
    mock_data = {
        'NewBeaconType': current_beacontype,
        'NewX_AVM-DE_PossibleBeaconTypes': 'None,11i,WPAand11i,11iandWPA3',
        'NewSSID': ssid,
        'NewKeyPassphrase': password,
    }
    instance = WLANConfigMock(mock_data)
    stream = get_wifi_qr_code(instance, kind="png", security=security)
    fname = write_stream_to_tempfile(stream)
    result = get_content_from_qr_file(fname)
    os.unlink(fname)  # do this asap
    assert result == expected_result
