"""
Module handling the SOAP based communication with the router.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import datetime
import re

import requests
from requests.auth import HTTPDigestAuth
from xml.etree import ElementTree as etree

from .exceptions import (
    FritzConnectionException,
    FRITZ_ERRORS,
)
from .utils import localname


SOAP_NS = "http://schemas.xmlsoap.org/soap/envelope/"


def datetime_convert(value):
    """Converts a string in ISO 8601 format to a datetime-object."""
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S')
    except ValueError:
        return value


def boolean_convert(value):
    """Converts a string like '1' or '0' to a boolean value"""
    try:
        return bool(int(value))
    except ValueError:
        # should not happen: leave value as is
        return value


def uuid_convert(value):
    """Strips the leading 'uuid:' part from the string."""
    return value.split(':')[-1]


def raise_fritzconnection_error(response):
    """
    Handles all responses with status codes other than 200.
    Will raise the relevant FritzConnectionException with
    the error code and description if available
    """
    parts = []
    error_code = None
    try:
        root = etree.fromstring(response.content)
    except etree.ParseError:
        # May fail in case it's html instead of xml.
        # Can happen on wrong authentication.
        # That means it is not an error reported from executing
        # some service in the box, but rather not allowed to
        # access the box at all.
        # Whatever it is, report it here:
        detail = re.sub(r'<.*?>', '', response.text)
        msg = f'Unable to perform operation. {detail}'
        raise FritzConnectionException(msg)
    detail = root.find('.//detail')
    children = detail.iter()
    next(children) # skip detail itself
    for node in children:
        tag = localname(node)
        text = node.text.strip()
        if tag == "errorCode":
            error_code = text
        parts.append(f'{tag}: {text}')
    message = '\n'.join(parts)
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
    parameters will get set by FritzConnection,)
    """

    headers = {
        'soapaction': '',
        'content-type': 'text/xml',
        'charset': 'utf-8'
    }

    envelope = re.sub(r'\s +', '', """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">{body}
        </s:Envelope>
        """)

    body_template = re.sub(r'\s +', '', """
        <s:Body>
        <u:{action_name} xmlns:u="{service_type}">{arguments}
        </u:{action_name}>
        </s:Body>
        """)

    argument_template = "<s:{name}>{value}</s:{name}>"
    method = 'post'

    conversion_table = {
        'datetime': datetime_convert,
        'boolean': boolean_convert,
        'uuid': uuid_convert,
        'i4': int,
        'ui1': int,
        'ui2': int,
        'ui4': int,
    }

    def __init__(self, address, port, user, password,
                 timeout=None, session=None):
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
            arguments=arguments
        )

    def execute(self, service, action_name, arguments):
        """
        Builds the soap request and returns the response as dictionary.
        Numeric and boolean values are converted from strings to Python
        datatypes.
        """
        def handle_response(response):
            if response.status_code != 200:
                raise_fritzconnection_error(response)
            return self.parse_response(response, service, action_name)

        headers = self.headers.copy()
        headers['soapaction'] = f'{service.serviceType}#{action_name}'
        arguments = ''.join(self.argument_template.format(name=k, value=v)
                            for k, v in arguments.items())
        body = self.get_body(service, action_name, arguments)
        envelope = self.envelope.format(body=body)
        url = f'{self.address}:{self.port}{service.controlURL}'
        auth = None
        if self.password:
            auth = HTTPDigestAuth(self.user, self.password)
        if self.session:
            with self.session.post(
                url, data=envelope, headers=headers, auth=auth
            ) as response:
                return handle_response(response)
        else:
            response = requests.post(
                url, data=envelope, headers=headers, auth=auth,
                timeout=self.timeout, verify=False)
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
                value = root.find(f'.//{argument_name}').text
            except AttributeError:
                continue
            state_variable_name = \
                action.arguments[argument_name].relatedStateVariable
            state_variable = service.state_variables[state_variable_name]
            data_type = state_variable.dataType.lower()
            try:
                value = self.conversion_table[data_type](value)
            except KeyError:
                pass
            result[argument_name] = value
        return result
