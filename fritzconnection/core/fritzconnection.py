"""
fritzconnection.py

Module to communicate with the AVM Fritz!Box.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT - tldr: USAGE IS FREE AND ENTIRELY AT OWN RISK!
Author: Klaus Bremer
"""


import os
import string

from .devices import DeviceManager
from .soaper import Soaper


# FritzConnection defaults:
FRITZ_IP_ADDRESS = '169.254.1.1'
FRITZ_TCP_PORT = 49000
FRITZ_IGD_DESC_FILE = 'igddesc.xml'
FRITZ_TR64_DESC_FILE = 'tr64desc.xml'
FRITZ_USERNAME = 'dslf-config'


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

        self.soaper = Soaper(address, port, user, password)
        self.device_manager = DeviceManager()

        descriptions = [FRITZ_IGD_DESC_FILE]
        if password:
            descriptions.append(FRITZ_TR64_DESC_FILE)
        for description in descriptions:
            source = f'http://{address}:{port}/{description}'
            try:
                self.device_manager.add_description(source)
            except OSError:
                # resource not available: ignore this
                pass

        self.device_manager.scan()
        self.device_manager.load_service_descriptions(address, port)

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
        dictionary given to 'arguments' or as separate keyword
        parameters. If 'arguments' is given additional
        keyword-parameters as further arguments are ignored.
        If the service_name does not end with a number (like 1), a 1
        gets added by default. If the service_name ends with a colon and a
        number, the colon gets removed. So i.e. WLANConfiguration
        expands to WLANConfiguration1 and WLANConfiguration:2 converts
        to WLANConfiguration2.
        Invalid service names will raise a ServiceError and invalid
        action names will raise an ActionError.
        """
        arguments = arguments if arguments else dict()
        if not arguments:
            arguments.update(kwargs)
        service_name = self.normalize_name(service_name)
        try:
            service = self.device_manager.services[service_name]
        except KeyError:
            raise FritzServiceError(f'unknown service: "{service_name}"')
        return self.soaper.execute(service, action_name, arguments)

    def reconnect(self):
        """
        Terminate the connection and reconnects with a new ip.
        """
        self.call_action('WANIPConn1', 'ForceTermination')