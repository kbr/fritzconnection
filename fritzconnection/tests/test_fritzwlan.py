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
        