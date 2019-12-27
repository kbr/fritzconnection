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


def get_content_from(url, timeout=None):
    conn = requests.get(url, timeout=timeout)
    ct = conn.headers.get("Content-type")
    if ct == "text/html":
        raise FritzConnectionException("Unable to login into device to get configuration information.")
    return conn.text


def get_xml_root(source, timeout=None):
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
        source = get_content_from(source, timeout=timeout)
    elif not source.startswith("<"):
        # assume it's a filename
        with open(source) as fobj:
            source = fobj.read()
    return etree.fromstring(source)
