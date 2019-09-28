"""
fritzconnection 1.0
requires Python >= 3.6
"""


__version__ = '1.0_alpha_1'


import os
import string

import requests
from requests.auth import HTTPDigestAuth

from lxml import etree

from .nodes import (
    Description,
)


# FritzConnection defaults:
FRITZ_IP_ADDRESS = '169.254.1.1'
FRITZ_TCP_PORT = 49000
FRITZ_IGD_DESC_FILE = 'igddesc.xml'
FRITZ_TR64_DESC_FILE = 'tr64desc.xml'
FRITZ_USERNAME = 'dslf-config'


def get_version():
    """returns the module version"""
    return __version__


# ---------------------------------------------------------
# fritzconnection specific exceptions:
# ---------------------------------------------------------

class FritzConnectionException(Exception):
    """Base Exception for communication errors with the Fritz!Box"""


class ActionError(FritzConnectionException):
    """Exception raised by calling nonexisting actions."""


class ServiceError(FritzConnectionException):
    """Exception raised by calling nonexisting services."""



# ---------------------------------------------------------
# DeviceManager:
# separate class for better testing
# ---------------------------------------------------------

class DeviceManager:
    """
    Knows all data about the device and the sub-devices, including the
    available services.
    """

    def __init__(self):
        self.descriptions = []
        self.services = {}

    @property
    def modelname(self):
        """
        Take the root-device of the first description and return the
        according modelname. This is the name of the Fritz!Box itself.
        Will raise an IndexError if the method is called before
        descriptions are added.
        """
        return self.descriptions[0].device_model_name

    def add_description(self, source):
        """
        Adds description data about the devices and the according
        services. 'source' is a string with the xml-data, like the
        content of an igddesc- or tr64desc-file.
        """
        tree = etree.parse(source)
        root = tree.getroot()
        self.descriptions.append(Description(root))

    def scan(self):
        """
        Scans all available services defined by the description files.
        Must get called after all xml-descriptions are added.
        """
        for description in self.descriptions:
            self.services.update(description.services)


# ---------------------------------------------------------
# Connector:
# handles the soap based connection to the FritzBox
# ---------------------------------------------------------

class Soaper:
    """
    Class that handles the soap based communication with the FritzBox.
    """

    header = {
        'soapaction': '',
        'content-type': 'text/xml',
        'charset': 'utf-8'
    }

    envelope = """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">{body}
        </s:Envelope>""".strip()

    argument_template = "<s:{name}>{value}</s:{name}>"
    method = 'post'

    def __init__(self, address, port, user, password):
        self.address = address
        self.port = port
        self.user = user
        self.password = password

    def get_body(self, service, action_name, arguments):
        body = f'<s:Body>'\
               f'<u:{action_name} xmlns:u="{service.serviceType}">{arguments}'\
               f'</u:{action_name}></s:Body>'
        return body.strip()

    def execute(self, service, action_name, arguments):
        header = self.header.copy()
        header['soapaction'] = f'{service.serviceType}#{action_name}'
        arguments = ''.join(self.argument_template.format(name=k, value=v)
                            for k, v in arguments.items())
        body = self.get_body(service, action_name, arguments)
        envelope = self.envelope.format(body=body)
        return envelope





# ---------------------------------------------------------
# core class: FritzConnection
# ---------------------------------------------------------

class FritzConnection:

    def __init__(self, address=None, port=None, user=None, password=None):
        """
        Initialisation of FritzConnection: reads all data from the box
        and also the api-description (the servicenames and according
        actionnames as well as the parameter-types) that can vary among
        models and stores these informations as instance-attributes.
        This can be an expensive operation. Because of this an instance
        of FritzConnection should be created once and reused in an
        application. All parameters are optional. But if there is more
        than one FritzBox in the network, an address (ip as string) must
        be given, otherwise it is not defined which box may respond. If
        no user is given the Environment gets checked for a
        FRITZ_USERNAME setting. If there is no entry in the environment
        the avm-default-username will be used. If no password is given
        the Environment gets checked for a FRITZ_PASSWORD setting. So
        password can be used without using configuration-files or even
        hardcoding.
        """
        if address is None:
            address = FRITZ_IP_ADDRESS
        if port is None:
            port = FRITZ_TCP_PORT
        if user is None:
            user = os.getenv('FRITZ_USERNAME', FRITZ_USERNAME)
        if password is None:
            password = os.getenv('FRITZ_PASSWORD', '')

        self.address = address
        self.port = port
        self.user = user
        self.password = password
        self.soaper = Soaper(address, port, user, password)
        self.device_manager =  DeviceManager()

        descriptions = [FRITZ_IGD_DESC_FILE]
        if self.password:
            descriptions.append(FRITZ_TR64_DESC_FILE)
        for description in descriptions:
            source = f'http://{self.address}:{self.port}/{description}'
            try:
                self.device_manager.add_description(source)
            except OSError:
                # resource not available: ignore this
                pass
        self.device_manager.scan()

    def __repr__(self):
        """Return a readable representation"""
        return f'{self.device_manager.modelname} at ip {self.address}'

    @staticmethod
    def normalize_name(name):
        if ':' in name:
            name, number = name.split(':', 1)
            name = name + number
        elif name[-1] not in string.digits:
            name = name + '1'
        return name

    # -------------------------------------------
    # public api:
    # -------------------------------------------

    def call_action(self, service_name, action_name, *,
                    arguments=None, **kwargs):
        """
        Executes the given action of the given service. Both parameters
        are required. Arguments are optional and can be provided as a
        dictionary given to 'arguments' or as single keyword parameters.
        If the service_name does not end with a number (like 1), a 1
        gets added by default. If the serve_name ends with a colon and a
        number, the colon gets removed. So i.e. WLANConfiguration
        expands to WLANConfiguration1 and WLANConfiguration:2 converts
        to WLANConfiguration2.
        Invalid service names or action names will raise a ServiceError
        resp. an ActionError.
        """
        arguments = arguments if arguments else dict()
        arguments.update(kwargs)
        service_name = self.normalize_name(service_name)
        try:
            service = self.device_manager.services[service_name]
        except KeyError:
            raise ServiceError(f'unknown service: "{service_name}"')
        return self.soaper.execute(service, action_name, arguments)

