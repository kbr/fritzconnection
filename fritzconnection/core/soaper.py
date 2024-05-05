"""
Module handling the SOAP based communication with the router.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import datetime
import html
import re

import requests
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree as etree

from .exceptions import (
    FritzAuthorizationError,
    FritzConnectionException,
    FRITZ_ERRORS,
)
from .logger import fritzlogger
from .utils import localname


SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"
STATUS_UNAUTHORIZED = 401


def datetime_convert(value):
    """
    Converts a string in ISO 8601 format to a datetime-object.
    Raise ValueError if value does not match ISO 8601.
    """
    return datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")


def boolean_convert(value):
    """
    Converts a string like '1' or '0' to a boolean value.
    Raise ValueError if it is something else than '1' or '0', because
    this violates the data_type according to the AVM documentation.
    """
    if value == "1" or value == "0":
        return bool(int(value))
    msg = f"value '{value}' does not match '1' or '0'."
    raise ValueError(msg)


def uuid_convert(value):
    """Strips the leading 'uuid:' part from the string."""
    return value.split(":")[-1]


CONVERSION_TABLE = {
    "datetime": datetime_convert,
    "boolean": boolean_convert,
    "uuid": uuid_convert,
    "i4": int,
    "ui1": int,
    "ui2": int,
    "ui4": int,
}


def get_converted_value(data_type, value):
    """
    Try to convert the value from string to the given data_type. The
    data_type is used as key in the CONVERSION_TABLE dictionary. In case
    the data_type is unknown, the original value is returned.
    """
    try:
        return CONVERSION_TABLE[data_type](value)
    except KeyError:
        return value


def encode_boolean(value):
    """
    Returns 1 or 0 if the value is True or False.
    None gets interpreted as False.
    Otherwise, the original value is returned.
    """
    if value is True:
        return 1
    if value is False or value is None:
        return 0
    return value


def get_html_safe_value(value):
    """
    Returns a xml `encoded value` if it's an encodable value.
    `value` can be of any type. If it is a boolean or None it
    gets converted to the integer 1 or 0.
    If it is a string the characters in the set `&<>'"` are
    converted to html-safe sequences.
    Any other datatype gets returned as is.
    """
    value = encode_boolean(value)
    if isinstance(value, str):
        value = html.escape(value)
    return value


def preprocess_arguments(arguments):
    """
    Takes a dictionary with arguments for a soap call and converts all
    values which are True, False or None to the according integers:
    1, 0, 0.
    Returns a new dictionary with the processed values.
    """
    return {k: get_html_safe_value(v) for k, v in arguments.items()}


def get_argument_value(root, argument_name):
    """
    Takes an etree-root object, which is a parsed soap-response from the
    Fritz!Box, and an argument_name, which corresponds to a node-name in
    the element-tree hierarchy. Returns the text-attribute of the node
    as a string.
    Raise an AttributeError in case that a node is not found.
    """
    # root.find will() raise the AttributeError on unknown nodes
    value = root.find(f".//{argument_name}").text
    if value is None:
        # this will be the case on empty tags: <tag></tag>
        value = ""
    return value


def is_html_response(text):
    """
    Returns a boolean whether the raw response text starts with an
    html-tag.
    """
    return text.casefold().startswith("<html")


def remove_html_tags(text):
    """
    Returns the given string `response_text` with all tags removed.
    """
    tag_free = re.sub(r"<.*?>", " ", text)
    return re.sub(r" +", " ", tag_free).strip()  # make it nice


def raise_fritzconnection_error(response):
    """
    Handles all responses with status codes other than 200.
    Will raise a FritzConnectionException with the error code and
    description if available. Can also raise a FritzAuthorizationError
    in case of 401 html-response status code.
    """
    parts = []
    error_code = None

    if is_html_response(response.text):
        # if it is an html response, the error is described in the
        # body part: remove all tags and provide the result as
        # error-message:
        detail = remove_html_tags(response.text)
        msg = f"Unable to perform operation. {detail}"
        if response.status_code == STATUS_UNAUTHORIZED:
            raise FritzAuthorizationError(msg)
        raise FritzConnectionException(msg)

    # otherwise the content is xml and the error-description
    # is part of the structured xml info:
    try:
        root = etree.fromstring(response.content)
    except etree.ParseError as err:
        # should not happen (at least not observed so far)
        raise FritzConnectionException(str(err))

    # extract error information from the provided xml data
    detail = root.find(".//detail")
    children = detail.iter()
    next(children)  # skip detail itself
    for node in children:
        tag = localname(node)
        text = node.text.strip()
        if tag == "errorCode":
            error_code = text
        parts.append(f"{tag}: {text}")
    message = "\n".join(parts)
    # try except:KeyError not possible,
    # because one of the raised Exceptions may inherit from KeyError.
    exception = FRITZ_ERRORS.get(error_code, FritzConnectionException)
    raise exception(message)


class Soaper:
    """
    Class making the soap on its own to communicate with the FritzBox.
    Instead of ham, spam and eggs, it's hopelessly addicted to soap.

    For accessing the Fritz!Box the parameters `address` for the router
    ip, `port`, `user`, `password` and `session` are required. (These
    parameters will get set by FritzConnection.)
    """

    headers = {"soapaction": "", "content-type": "text/xml", "charset": "utf-8"}

    envelope = re.sub(
        r"\s +",
        "",
        """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">{body}
        </s:Envelope>
        """,
    ).replace('/"xmlns:', '/" xmlns:')

    body_template = re.sub(
        r"\s +",
        "",
        """
        <s:Body>
        <u:{action_name} xmlns:u="{service_type}">{arguments}
        </u:{action_name}>
        </s:Body>
        """,
    )

    argument_template = "<{name}>{value}</{name}>"
    method = "post"

    conversion_table = {
        "datetime": datetime_convert,
        "boolean": boolean_convert,
        "uuid": uuid_convert,
        "i4": int,
        "ui1": int,
        "ui2": int,
        "ui4": int,
    }

    def __init__(self, address, port, user, password, timeout=None, session=None):
        self.address = address
        self.port = port
        self.user = user
        self.password = password
        self.timeout = timeout
        self.session = session

    def get_body(self, service, action_name, arguments):
        """Returns the body by template substitution."""
        return self.body_template.format(
            service_type=service.serviceType,
            action_name=action_name,
            arguments=arguments,
        )

    def execute(self, service, action_name, arguments):
        """
        Builds the soap request and returns the response as dictionary.
        Numeric and boolean values are converted from strings to Python
        datatypes.
        """

        def handle_response(response):
            fritzlogger.debug(f"response status: {response.status_code}")
            fritzlogger.debug(response.text)
            if response.status_code != 200:
                raise_fritzconnection_error(response)
            return self.parse_response(response, service, action_name)

        headers = self.headers.copy()
        headers["soapaction"] = f"{service.serviceType}#{action_name}"
        arguments = preprocess_arguments(arguments)
        arguments = "".join(
            self.argument_template.format(name=k, value=v) for k, v in arguments.items()
        )
        body = self.get_body(service, action_name, arguments)
        envelope = self.envelope.format(body=body).encode("utf-8")
        url = f"{self.address}:{self.port}{service.controlURL}"
        fritzlogger.debug(f"\n{url}")
        fritzlogger.debug(envelope)
        if self.session:
            with self.session.post(
                url, data=envelope, headers=headers, timeout=self.timeout
            ) as response:
                return handle_response(response)
        else:
            if self.password:
                auth = HTTPDigestAuth(self.user, self.password)
            else:
                auth = None
            response = requests.post(
                url,
                data=envelope,
                headers=headers,
                auth=auth,
                timeout=self.timeout,
                verify=False,
            )
            return handle_response(response)

    def parse_response(self, response, service, action_name):
        """
        Extracts all known parameters of the given action from the
        response and returns this as a dictionary with the out-parameter
        names as keys and the corresponding response as values.
        Will raise an ActionError on unknown action_name.
        """
        result = dict()
        action = service.actions[action_name]
        root = etree.fromstring(response.content)
        for argument_name in action.arguments:
            try:
                value = get_argument_value(root, argument_name)
            except AttributeError:
                continue
            state_variable_name = action.arguments[argument_name].relatedStateVariable
            state_variable = service.state_variables[state_variable_name]
            data_type = state_variable.dataType.lower()
            try:
                value = get_converted_value(data_type, value)
            except ValueError:
                # ignore malformed value and return 'as is'.
                pass
            result[argument_name] = value
        return result
