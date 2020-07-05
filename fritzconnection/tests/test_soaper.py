import datetime
from xml.etree import ElementTree as etree

import pytest

from ..core.exceptions import (
    FRITZ_ERRORS,
    ActionError,
    ServiceError,
    FritzActionError,
    FritzArgumentError,
    FritzActionFailedError,
    FritzArgumentValueError,
    FritzOutOfMemoryError,
    FritzSecurityError,
    FritzArrayIndexError,
    FritzLookUpError,
    FritzArgumentStringToShortError,
    FritzArgumentStringToLongError,
    FritzArgumentCharacterError,
    FritzInternalError,
)

from ..core.soaper import (
    boolean_convert,
    encode_boolean,
    get_argument_value,
    get_converted_value,
    raise_fritzconnection_error,
)


content_template = """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <s:Fault>
      <faultcode>s:Client</faultcode>
      <faultstring>UPnPError</faultstring>
      <detail>
        <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
          <errorCode>{error_code}</errorCode>
          <errorDescription>Invalid Action</errorDescription>
        </UPnPError>
      </detail>
    </s:Fault>
  </s:Body>
</s:Envelope>
"""


class Response:
    """Namespace object."""


@pytest.mark.parametrize(
    "error_code, exception", [
        ('401', FritzActionError),
        ('402', FritzArgumentError),
        ('501', FritzActionFailedError),
        ('600', FritzArgumentValueError),
        ('603', FritzOutOfMemoryError),
        ('606', FritzSecurityError),
        ('713', FritzArrayIndexError),
        ('714', FritzLookUpError),
        ('801', FritzArgumentStringToShortError),
        ('802', FritzArgumentStringToLongError),
        ('803', FritzArgumentCharacterError),
        ('820', FritzInternalError),

        ('713', IndexError),
        ('714', KeyError),

        ('401', ActionError),

    ]
)
def test_raise_fritzconnection_error(error_code, exception):
    """check for exception raising depending on the error_code"""
    content = content_template.format(error_code=error_code)
    response = Response()
    response.content = content.encode()
    pytest.raises(exception, raise_fritzconnection_error, response)


@pytest.mark.parametrize(
    "value, expected_result", [
        ('0', False),
        ('1', True),
    ]
)
def test_boolean_convert(value, expected_result):
    result = boolean_convert(value)
    assert result == expected_result


@pytest.mark.parametrize(
    "value", ['2', 'x', '3.1']
)
def test_boolean_convert_fails(value):
    with pytest.raises(ValueError):
        boolean_convert(value)


long_error = """
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <s:Fault>
      <faultcode> s:Client </faultcode>
      <faultstring>
UPnPError </faultstring>
      <detail>
        <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
          <errorCode> 401 </errorCode>
          <errorDescription> Invalid Action </errorDescription>
        </UPnPError>
      </detail>
    </s:Fault>
  </s:Body>
</s:Envelope>
"""


def test_long_error_message():
    response = Response()
    response.content = long_error.encode()
    with pytest.raises(ActionError) as exc:
        raise_fritzconnection_error(response)

    assert exc.value.args[0] == "\n".join(
        ["UPnPError: ",
         "errorCode: 401",
         "errorDescription: Invalid Action",
         ]
    )


@pytest.mark.parametrize(
    "value, expected_type", [
        ("text", str),
        (0, int),
        (1, int),
        (None, int),
        (False, int),
        (True, int),
    ]
)
def test_encode_boolean(value, expected_type):
    result = encode_boolean(value)
    assert isinstance(result, expected_type)


@pytest.mark.parametrize(
    "value, not_expected_type", [
        (False, bool),  # should be int after encoding, not bool
        (True, bool),
    ]
)
def test_encode_boolean2(value, not_expected_type):
    result = encode_boolean(value)
    assert not isinstance(result, not_expected_type)


soap_root = etree.fromstring("""<?xml version="1.0"?>
<data>
    <container>
        <year>2010</year>
        <msg>message text</msg>
        <number>3.141</number>
        <ip></ip>
    </container>
</data>""")


@pytest.mark.parametrize(
    "argument_name, expected_value", [
        ('year', '2010'),
        ('msg', 'message text'),
        ('number', '3.141'),
        ('ip', ''),
    ]
)
def test_get_argument_value(argument_name, expected_value):
     value = get_argument_value(soap_root, argument_name)
     assert value == expected_value


@pytest.mark.parametrize(
    "data_type, value, expected_value", [
        ('datetime', '2020-02-02T10:10:10', datetime.datetime(2020, 2, 2, 10, 10, 10)),
        ('boolean', '1', True),
        ('boolean', '0', False),
        ('uuid', 'uuid:123', '123'),
        ('uuid', '123', '123'),
        ('i4', '42', 42),
        ('ui1', '42', 42),
        ('ui2', '42', 42),
        ('ui4', '42', 42),
    ]
)
def test_get_converted_value(data_type, value, expected_value):
    result = get_converted_value(data_type, value)
    assert result == expected_value


@pytest.mark.parametrize(
    "data_type, value", [
        ('datetime', '2010.02.02-10:10:10'),  # not ISO 8601
        ('boolean', ''),  # neither '1' nor '0'
    ]
)
def test_get_converted_value_fails(data_type, value):
    with pytest.raises(ValueError):
        get_converted_value(data_type, value)
