
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

from ..core.fritzconnection import raise_fritzconnection_error


content_template = """<?xml version="1.0"?>\n<s:Envelope
xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
<s:Body>\n<s:Fault>\n<faultcode>s:Client</faultcode>
<faultstring>UPnPError</faultstring>
<detail>\n<UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
<errorCode>{error_code}</errorCode>
<errorDescription>Invalid Action</errorDescription>
</UPnPError>\n</detail>\n</s:Fault>\n</s:Body>\n</s:Envelope>"""


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
