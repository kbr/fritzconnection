"""
Common functions for other core-modules.
"""

import re
import requests

from xml.etree import ElementTree as etree
from .exceptions import FritzConnectionException


NS_REGEX = re.compile("({(?P<namespace>.*)})?(?P<localname>.*)")


def localname(node):
    if callable(node.tag):
        return "comment"
    m = NS_REGEX.match(node.tag)
    return m.group('localname')


def get_content_from(url, timeout=None, session=None):
    """
    Returns text from a get-request for the given url. In case of a
    secure request (using TLS) the parameter verify is set to False, to
    disable certificate verifications. As the Fritz!Box creates a
    self-signed certificate for use in the LAN, encryption will work but
    verification will fail.
    """
    def handle_response(response):
        ct = response.headers.get("Content-type")
        if ct == "text/html":
            message = f"Unable to retrieve resource '{url}' from the device."
            raise FritzConnectionException(message)
        return response.text

    if session:
        with session.get(url) as response:
            return handle_response(response)
    response = requests.get(url, timeout=timeout, verify=False)
    return handle_response(response)


def get_xml_root(source, timeout=None, session=None):
    """
    Function to help migrate from lxml to the standard-library xml-package.

    'source' must be a string and can be an xml-string, a uri or a file
    name. `timeout` is an optional parameter limiting the time waiting
    for a router response.
    In all cases this function returns an xml.etree.Element instance
    which is the root of the parsed tree.
    """
    if source.startswith("http://") or source.startswith("https://"):
        # it's a uri, use requests to get the content
        source = get_content_from(source, timeout=timeout, session=session)
    elif not source.startswith("<"):
        # assume it's a filename
        with open(source) as fobj:
            source = fobj.read()
    return etree.fromstring(source)
