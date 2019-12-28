"""
Common functions for other core-modules.
"""

import re
import requests

from xml.etree import ElementTree as etree
from .exceptions import FritzConnectionException

from requests.adapters import HTTPAdapter


# adapted from https://github.com/urllib3/urllib3/issues/517
class HostnameVerificationAdapter(requests.adapters.HTTPAdapter):
    def __init__(self, *args, assert_hostname=None, **kwargs):
        self.assert_hostname = assert_hostname
        requests.adapters.HTTPAdapter.__init__(self, *args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        self.poolmanager = requests.adapters.PoolManager(*args, assert_hostname=self.assert_hostname, **kwargs)


NS_REGEX = re.compile("({(?P<namespace>.*)})?(?P<localname>.*)")


def localname(node):
    if callable(node.tag):
        return "comment"
    m = NS_REGEX.match(node.tag)
    return m.group('localname')


def get_content_from(url, timeout=None, certificate=None, session=None):
    if certificate is not None:
        conn = session.get(url, verify=certificate, timeout=timeout)
    else:
        conn = session.get(url, timeout=timeout)

    ct = conn.headers.get("Content-type")
    if ct == "text/html":
        raise FritzConnectionException("Unable to login into device to get configuration information.")
    return conn.text


def get_xml_root(source, timeout=None, certificate=None, session=None):
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
        source = get_content_from(source, timeout=timeout, certificate=certificate, session=session)
    elif not source.startswith("<"):
        # assume it's a filename
        with open(source) as fobj:
            source = fobj.read()
    return etree.fromstring(source)
