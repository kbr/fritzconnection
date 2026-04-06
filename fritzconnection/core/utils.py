"""
Common functions for other core-modules.
"""

from __future__ import annotations

import os
import re
from typing import Any, cast
from xml.etree import ElementTree as etree

import requests
from requests import Response, Session

from .exceptions import FritzConnectionException, FritzResourceError
from .logger import fritzlogger


NS_REGEX = re.compile("({(?P<namespace>.*)})?(?P<localname>.*)")
VALUES_TRUE = {"true", "on", "1"}
VALUES_FALSE = {"false", "off", "0"}

def localname(node: etree.Element) -> str:
    if callable(node.tag):
        return "comment"
    tag = node.tag
    m = NS_REGEX.match(tag)
    if m is None:
        return tag
    local = m.group('localname')
    return local if local is not None else tag

def get_content_from(
    url: str,
    timeout: float | None = None,
    session: Session | None = None,
) -> str:
    """
    Returns text from a get-request for the given url. In case of a
    secure request (using TLS) the parameter verify is set to False, in order to
    disable certificate verifications. As the Fritz!Box creates a
    self-signed certificate for use in the LAN, encryption will work but
    verification will fail.
    """
    def handle_response(response: Response) -> str:
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

    def do_request() -> str:
        fritzlogger.debug(f"requesting: {url}")
        if session is not None:
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


def get_xml_root(
    source: str,
    timeout: float | None = None,
    session: Session | None = None,
) -> etree.Element:
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


def boolean_from_string(value: str) -> bool:
    """
    Takes a value as a string and converts it to a boolean or None. The
    string could be "true" or "false" in upper-, lower- and mixed-case.
    Also "on", "off" and "0", "1" are converted. If the value can not
    converted a ValueError gets raised. If the value does not support
    the .lower() method, an AttributeError gets raised.
    """
    lower_value = value.lower()
    if lower_value in VALUES_TRUE:
        return True
    if lower_value in VALUES_FALSE:
        return False
    raise ValueError(f"can't convert '{lower_value}' to a boolean.")


def get_boolean_from_string(value: str | None, default: bool | None = None) -> bool | None:
    """
    Same as `boolean_from_string` but returns the `default` argument
    instead of raising an exception.
    """
    if value is None:
        return default
    try:
        return boolean_from_string(value)
    except (AttributeError, ValueError):
        return default


def get_bool_env(key: str, default: bool | None = None) -> bool | None:
    """
    Return the value of the environment variable key converted to a
    boolean if it exists, or default if it doesn’t or can't get
    converted to a boolean. keys convertable to a boolean are "true",
    "on", "1" and "false", "off", "0".
    """
    value = os.getenv(key)
    return get_boolean_from_string(value, default)
