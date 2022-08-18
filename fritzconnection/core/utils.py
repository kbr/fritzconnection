"""
Common functions for other core-modules.
"""

import re
from types import SimpleNamespace
from xml.etree import ElementTree as etree

import requests

from .exceptions import FritzConnectionException, FritzResourceError
from .logger import fritzlogger


NS_REGEX = re.compile("({(?P<namespace>.*)})?(?P<localname>.*)")


def localname(node):
    if callable(node.tag):
        return "comment"
    m = NS_REGEX.match(node.tag)
    return m.group('localname')


def get_content_from(url, timeout=None, session=None):
    """
    Returns text from a get-request for the given url. In case of a
    secure request (using TLS) the parameter verify is set to False, in order to
    disable certificate verifications. As the Fritz!Box creates a
    self-signed certificate for use in the LAN, encryption will work but
    verification will fail.
    """
    def handle_response(response):
        fritzlogger.debug(response.text)
        ct = response.headers.get("Content-type")
        if ct == "text/html":
            message = f"Unable to retrieve resource '{url}' from the device."
            # this error will get catched, because it may happen depending
            # on the used router model, without doing any harm.
            # However it's logged on INFO level:
            fritzlogger.info(message)
            raise FritzResourceError(message)
        return response.text

    def do_request():
        fritzlogger.debug(f"requesting: {url}")
        if session:
            with session.get(url, timeout=timeout) as response:
                return handle_response(response)
        response = requests.get(url, timeout=timeout, verify=False)
        return handle_response(response)

    try:
        return do_request()
    except requests.exceptions.ConnectionError as err:
        message = f"Unable to get a connection: {err}"
        # that's an error worth logging:
        fritzlogger.error(message)
        # raise from None because the message holds the
        # proper information about the connection failure:
        raise FritzConnectionException(message) from None


def get_xml_root(source, timeout=None, session=None):
    """
    Function to help migrate from lxml to the standard-library xml-package.

    'source' must be a string and can be a xml-string, a uri or a file
    name. `timeout` is an optional parameter limiting the time waiting
    for a router response.
    In all cases this function returns a xml.etree.Element instance
    which is the root of the parsed tree.
    """
    if source.startswith("http://") or source.startswith("https://"):
        # it's an uri, use requests to get the content
        source = get_content_from(source, timeout=timeout, session=session)
    elif not source.startswith("<"):
        # assume it's a filename
        with open(source) as fobj:
            source = fobj.read()
    return etree.fromstring(source)


class ArgumentNamespace(SimpleNamespace):
    """
    Namespace object that also behaves like a dictionary.

    Usecase is as a wrapper for the dictionary returned from
    `FritzConnection.call_action()`. This dictionary has keys named
    "arguments" as described by the AVM documentation, combined with
    values as the corresponding return values. Instances of
    `ArgumentNamespace` can get used to extract a subset of this
    dictionary and transfer the Argument-names to more readable
    ones. For example consider that `fc` is a FritzConnection instance.
    Then the following call: ::

        result = fc.call_action("DeviceInfo1", "GetInfo")

    will return a dictionary like: ::

        {'NewManufacturerName': 'AVM',
         'NewManufacturerOUI': '00040E',
         'NewModelName': 'FRITZ!Box 7590',
         'NewDescription': 'FRITZ!Box 7590 154.07.29',
         'NewProductClass': 'AVMFB7590',
         'NewSerialNumber': '989BCB2B93B0',
         'NewSoftwareVersion': '154.07.29',
         'NewHardwareVersion': 'FRITZ!Box 7590',
         'NewSpecVersion': '1.0',
         'NewProvisioningCode': '000.044.004.000',
         'NewUpTime': 9516949,
         'NewDeviceLog': 'long string here ...'}

    In case that just the model name and serial number are of interest,
    and should have better names, first define a mapping: ::

        mapping = {
            "modelname": "NewModelName",
            "serial_number": "NewSerialNumber"
        }

    and use this `mapping` with the `result` to create an `ArgumentNamespace`
    instance: ::

        info = ArgumentNamespace(mapping, result)

    The `info` instance can now get used like a namespace object and
    like a dictionary: ::

        >>> info.serial_number
        >>> '989BCB2B93B0'

        >>> info['modelname']
        >>> 'FRITZ!Box 7590'

    """
    def __init__(self, mapping, source):
        super().__init__(
            **{name: source[attribute] for name, attribute in mapping.items()}
        )

    def __getitem__(self, key):
        return getattr(self, key)

