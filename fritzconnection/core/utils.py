"""
Common objects for other core-modules.
"""
import requests
from xml.etree import ElementTree as etree

from .exceptions import FritzConnectionException


def get_content_from(url):
    conn = requests.get(url)
    ct = conn.headers.get("Content-type")
    if ct == "text/html":
        raise FritzConnectionException("Unable to login into device to get configuration information.")
    return conn.text


def get_xml_root(source):
    """
    Function to help migrate from lxml to the standard-library xml-package.

    'source' must be a string and can be an xml-string, a uri or a file name.
    In all cases this function returns an xml.etree.Element instance
    which is the root of the parsed tree.
    """
    if source.startswith("http://") or source.startswith("https://"):
        # it's a uri, use requests to get the content
        source = get_content_from(source)
    elif not source.startswith("<"):
        # assume it's a filename
        with open(source) as fobj:
            source = fobj.read()
    return etree.fromstring(source)
