import datetime
from unittest.mock import patch
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
    Soaper,
    boolean_convert,
    encode_boolean,
    get_argument_value,
    get_converted_value,
    get_html_safe_value,
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
    "value, expected_results", [
        (True, 1),
        (False, 0),
        (None, 0),
        (3.141, 3.141),
        ("hello test", "hello test"),
        ("2021-07-17T12:00:00", "2021-07-17T12:00:00"),  # redundant, but ISO ;)
        ("ham, spam & eggs", "ham, spam &amp; eggs"),
        ("5 > 3", "5 &gt; 3"),
        ("3 < 5", "3 &lt; 5"),
        ('say "hello"', "say &quot;hello&quot;"),
        ("let's test again", ["let&apos; test again", "let&#x27;s test again"])
    ]
)
def test_get_html_safe_value(value, expected_results):
    if not isinstance(expected_results, list):
        expected_results = [expected_results]
    result = get_html_safe_value(value)
    assert result in expected_results


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


box_info_response = """
<j:BoxInfo xmlns:j="http://jason.avm.de/updatecheck/">
    <j:Name>FRITZ!Box 7590</j:Name>
    <j:HW>226</j:HW>
    <j:Version>100.01.01</j:Version>
    <j:Revision>10000</j:Revision>
    <j:Serial>000A0B000000</j:Serial>
    <j:OEM>avm</j:OEM>
    <j:Lang>de</j:Lang>
    <j:Annex>B</j:Annex>
    <j:Lab></j:Lab>
    <j:Country>049</j:Country>
    <j:Flag>mesh_master</j:Flag>
    <j:UpdateConfig>3</j:UpdateConfig>
</j:BoxInfo>
"""

def test_get_response():
    soap = Soaper("169.254.1.1", 49000, "admin", "pwd")
    response = Response()
    response.status_code = 200
    response.text = box_info_response
    response.content = box_info_response.encode()
    with patch("fritzconnection.core.soaper.requests.get", return_value=response) as request_mock:
        box_info = soap.get_response("jason_boxinfo.xml")
        assert box_info["Name"] == "FRITZ!Box 7590"
        assert box_info["Serial"] == "000A0B000000"
        request_mock.assert_called_once_with(
            "169.254.1.1/jason_boxinfo.xml", timeout=None, verify=False
        )
