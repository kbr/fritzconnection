import datetime
import types
from xml.etree import ElementTree as etree

import pytest

from ..core.exceptions import (
    ActionError,
    FritzAuthorizationError,
    FritzConnectionException,
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
    get_html_safe_value,
    is_html_response,
    raise_fritzconnection_error,
    redact_response,
    remove_html_tags,
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


@pytest.mark.parametrize(
    "error_code, status_code, exception", [
        ('401', 500, FritzActionError),
        ('402', 500, FritzArgumentError),
        ('501', 500, FritzActionFailedError),
        ('600', 500, FritzArgumentValueError),
        ('603', 500, FritzOutOfMemoryError),
        ('606', 500, FritzSecurityError),
        ('713', 500, FritzArrayIndexError),
        ('714', 500, FritzLookUpError),
        ('801', 500, FritzArgumentStringToShortError),
        ('802', 500, FritzArgumentStringToLongError),
        ('803', 500, FritzArgumentCharacterError),
        ('820', 500, FritzInternalError),

        ('713', 500, IndexError),
        ('714', 500, KeyError),

        ('401', 500, ActionError),

        (None, 401, FritzAuthorizationError),
        (None, 500, FritzConnectionException),

    ]
)
def test_raise_fritzconnection_error(error_code, status_code, exception):
    """check for exception raising depending on the error_code"""
    if error_code:
        content = content_template.format(error_code=error_code)
    else:
        content = '<html>some content</html>'
    response = types.SimpleNamespace()
    response.text = content
    response.content = content.encode()
    response.status_code = status_code
    pytest.raises(exception, raise_fritzconnection_error, response)


def test_raise_fritzauthorization_error():
    """check for exception raising depending on the html status code."""
    response = types.SimpleNamespace()
    response.content = b'<HTML><HEAD><TITLE>401 Unauthorized (ERR_NONE)</TITLE></HEAD><BODY><H1>401 Unauthorized</H1><BR>ERR_NONE<HR><B>Webserver</B> Sat, 01 Oct 2022 09:46:22 GMT</BODY></HTML>'
    response.text = '<HTML><HEAD><TITLE>401 Unauthorized (ERR_NONE)</TITLE></HEAD><BODY><H1>401 Unauthorized</H1><BR>ERR_NONE<HR><B>Webserver</B> Sat, 01 Oct 2022 09:46:22 GMT</BODY></HTML>'
    response.status_code = 401
    pytest.raises(FritzAuthorizationError, raise_fritzconnection_error, response)

    # simulate a http/500
    response.content = b'<HTML><HEAD><TITLE>500 internal error</TITLE></HEAD><BODY><H1>500 internal error</H1><BR>ERR_NONE<HR><B>Webserver</B> Sat, 01 Oct 2022 09:46:22 GMT</BODY></HTML>'
    response.text = '<HTML><HEAD><TITLE>500 internal error</TITLE></HEAD><BODY><H1>500 internal error</H1><BR>ERR_NONE<HR><B>Webserver</B> Sat, 01 Oct 2022 09:46:22 GMT</BODY></HTML>'
    response.status_code = 500
    pytest.raises(FritzConnectionException, raise_fritzconnection_error, response)


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


@pytest.mark.parametrize(
    "text, expected_result", [
        ('<html>something</html>', True),
        ('<?xml version= ...', False),
    ]
)
def test_is_html_response(text, expected_result):
    result = is_html_response(text)
    assert result == expected_result


@pytest.mark.parametrize(
    "text, expected_result", [
        ("funky", "funky"),
        ("funky funky", "funky funky"),
        ("funky  funky", "funky funky"),
        ("<bold>here</bold>", "here"),
        ("<bold>ham <i>spam</i><hr>and eggs </bold>", "ham spam and eggs"),
        (
            "<html><head>failure</head><body>something <b>very</b><hr /><i>strange</i></body></html>",
            "failure something very strange",
        )
    ]
)
def test_remove_html_tags(text, expected_result):
    result = remove_html_tags(text)
    assert result == expected_result


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
    response = types.SimpleNamespace()
    response.text = long_error
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

def test_redact_debug_log_phone_numbers():
    response = """
    <?xml version="1.0"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:GetInfoResponse xmlns:u="urn:dslforum-org:service:DeviceInfo:1">
    <NewManufacturerName>AVM</NewManufacturerName>
    <NewManufacturerOUI>00040E</NewManufacturerOUI>
    <NewModelName>FRITZ!Box 7530 AX</NewModelName>
    <NewDescription>FRITZ!Box 7530 AX Release 256.08.00</NewDescription>
    <NewProductClass>FRITZ!Box</NewProductClass>
    <NewSerialNumber>aabbccddeeff</NewSerialNumber>
    <NewSoftwareVersion>256.08.00</NewSoftwareVersion>
    <NewHardwareVersion>FRITZ!Box 7530 AX</NewHardwareVersion>
    <NewSpecVersion>1.0</NewSpecVersion>
    <NewProvisioningCode></NewProvisioningCode>
    <NewUpTime>86446</NewUpTime>
    <NewDeviceLog>
    23.11.24 12:28:10 Anmeldung der Internetrufnummer 491234567890 war nicht erfolgreich. Ursache: DNS-Fehler
    23.11.24 12:28:10 Anmeldung der Internetrufnummer 491234567891 war nicht erfolgreich. Ursache: DNS-Fehler
    23.11.24 12:28:10 Anmeldung der Internetrufnummer 491234567892 war nicht erfolgreich. Ursache: DNS-Fehler
    23.11.24 12:28:10 Anmeldung der Internetrufnummer 491234567893 war nicht erfolgreich. Ursache: DNS-Fehler
    </u:GetInfoResponse>
    </s:Body>
    </s:Envelope>
    """

    result = redact_response(False, response)
    assert result == response

    result = redact_response(True, response)
    assert result == """
    <?xml version="1.0"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:GetInfoResponse xmlns:u="urn:dslforum-org:service:DeviceInfo:1">
    <NewManufacturerName>AVM</NewManufacturerName>
    <NewManufacturerOUI>00040E</NewManufacturerOUI>
    <NewModelName>FRITZ!Box 7530 AX</NewModelName>
    <NewDescription>FRITZ!Box 7530 AX Release 256.08.00</NewDescription>
    <NewProductClass>FRITZ!Box</NewProductClass>
    <NewSerialNumber>aabbccddeeff</NewSerialNumber>
    <NewSoftwareVersion>256.08.00</NewSoftwareVersion>
    <NewHardwareVersion>FRITZ!Box 7530 AX</NewHardwareVersion>
    <NewSpecVersion>1.0</NewSpecVersion>
    <NewProvisioningCode></NewProvisioningCode>
    <NewUpTime>86446</NewUpTime>
    <NewDeviceLog>
    23.11.24 12:28:10 Anmeldung der Internetrufnummer ****** war nicht erfolgreich. Ursache: DNS-Fehler
    23.11.24 12:28:10 Anmeldung der Internetrufnummer ****** war nicht erfolgreich. Ursache: DNS-Fehler
    23.11.24 12:28:10 Anmeldung der Internetrufnummer ****** war nicht erfolgreich. Ursache: DNS-Fehler
    23.11.24 12:28:10 Anmeldung der Internetrufnummer ****** war nicht erfolgreich. Ursache: DNS-Fehler
    </u:GetInfoResponse>
    </s:Body>
    </s:Envelope>
    """

def test_redact_debug_log_external_ip_addresses():
    response = """
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:GetExternalIPAddressResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
    <NewExternalIPAddress>12.34.56.78</NewExternalIPAddress>
    </u:GetExternalIPAddressResponse>
    </s:Body>
    </s:Envelope>
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:X_AVM_DE_GetExternalIPv6AddressResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
    <NewExternalIPv6Address>0011:2233:4455:6677::0abcd</NewExternalIPv6Address>
    <NewPrefixLength>64</NewPrefixLength>
    <NewValidLifetime>0</NewValidLifetime>
    <NewPreferedLifetime>0</NewPreferedLifetime>
    </u:X_AVM_DE_GetExternalIPv6AddressResponse>
    </s:Body>
    </s:Envelope>
    """

    result = redact_response(False, response)
    assert result == response

    result = redact_response(True, response)
    assert result == """
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:GetExternalIPAddressResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
    <NewExternalIPAddress>******</NewExternalIPAddress>
    </u:GetExternalIPAddressResponse>
    </s:Body>
    </s:Envelope>
    <?xml version="1.0" encoding="utf-8"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:X_AVM_DE_GetExternalIPv6AddressResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">
    <NewExternalIPv6Address>******</NewExternalIPv6Address>
    <NewPrefixLength>64</NewPrefixLength>
    <NewValidLifetime>0</NewValidLifetime>
    <NewPreferedLifetime>0</NewPreferedLifetime>
    </u:X_AVM_DE_GetExternalIPv6AddressResponse>
    </s:Body>
    </s:Envelope>
    """

def test_redact_debug_log_wifi_passwords():
    response = """
    <?xml version="1.0"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:GetSecurityKeysResponse xmlns:u="urn:dslforum-org:service:WLANConfiguration:3">
    <NewWEPKey0>0123456789</NewWEPKey0>
    <NewWEPKey1></NewWEPKey1>
    <NewWEPKey2>01234 6789</NewWEPKey2>
    <NewWEPKey3></NewWEPKey3>
    <NewPreSharedKey>0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF0123456789ABCDEF</NewPreSharedKey>
    <NewKeyPassphrase>MY_GREAT_WIFI_PSK</NewKeyPassphrase>
    </u:GetSecurityKeysResponse>
    </s:Body>
    </s:Envelope>
    """

    result = redact_response(False, response)
    assert result == response

    result = redact_response(True, response)
    assert result == """
    <?xml version="1.0"?>
    <s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
    <s:Body>
    <u:GetSecurityKeysResponse xmlns:u="urn:dslforum-org:service:WLANConfiguration:3">
    <NewWEPKey0>******</NewWEPKey0>
    <NewWEPKey1>******</NewWEPKey1>
    <NewWEPKey2>******</NewWEPKey2>
    <NewWEPKey3>******</NewWEPKey3>
    <NewPreSharedKey>******</NewPreSharedKey>
    <NewKeyPassphrase>******</NewKeyPassphrase>
    </u:GetSecurityKeysResponse>
    </s:Body>
    </s:Envelope>
    """
