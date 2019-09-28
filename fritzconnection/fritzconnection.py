# -*- coding: utf-8 -*-

"""
fritzconnection.py

This is a tool to communicate with the FritzBox.
All availabel actions (aka commands) and corresponding parameters are
read from the xml-configuration files requested from the FritzBox. So
the available actions may change depending on the FritzBox model and
firmware.
The command-line interface allows the api-inspection.
The api can also be inspected by a terminal session:

>>> import fritzconnection as fc
>>> fc.print_api()

'print_api' takes the optional parameters:
    address = ip-address
    port = port number (should not change)
    user = the username
    password = password (to access tr64-services)

In most cases you have to provide the ip (in case you changed the
default or have multiple boxes i.e. for multiple WLAN access points).
Also you have to send the password to get the complete api.

License: MIT https://opensource.org/licenses/MIT
Source: https://github.com/kbr/fritzconnection
Author: Klaus Bremer
"""

# module level pylint settings:
# this is done here and not in a configuration file
# so that it is clear by reading the code, which errors are silenced
# or marked as not relevant.
# pylint: disable=useless-object-inheritance  # for python2 compatibility
# pylint: disable=c-extension-no-member  # don't freak out because of lxml


__version__ = '0.8.4'

import argparse
import os
import requests
from requests.auth import HTTPDigestAuth

from lxml import etree


# FritzConnection defaults:
FRITZ_IP_ADDRESS = '169.254.1.1'
FRITZ_TCP_PORT = 49000
FRITZ_IGD_DESC_FILE = 'igddesc.xml'
FRITZ_TR64_DESC_FILE = 'tr64desc.xml'
FRITZ_USERNAME = 'dslf-config'


def get_version():
    """returns the module version (aka. package version since 0.8.2)"""
    return __version__


# ---------------------------------------------------------
# Module specific exceptions:
# ---------------------------------------------------------

class FritzConnectionException(Exception):
    """Base Exception for communication errors with the Fritz!Box"""


class ServiceError(FritzConnectionException):
    """Exception raised by calling nonexisting services."""


class ActionError(FritzConnectionException):
    """Exception raised by calling a nonexisting action for a given service."""


class AuthorizationError(FritzConnectionException):
    """
    Exception raised by calling a service that requires a password
    without a password or a wrong one.
    """


# ---------------------------------------------------------
# The core classes of fritzconnection:
# ---------------------------------------------------------

class FritzAction(object):
    """
    Class representing an action (aka command).
    Knows how to execute itself.
    Access to any password-protected action must require HTTP digest
    authentication.
    See: http://www.broadband-forum.org/technical/download/TR-064.pdf
    """
    header = {'soapaction': '',
              'content-type': 'text/xml',
              'charset': 'utf-8'}
    envelope = """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">%s
        </s:Envelope>
        """
    body_template = """
        <s:Body>
        <u:%(action_name)s xmlns:u="%(service_type)s">%(arguments)s
        </u:%(action_name)s>
        </s:Body>
        """
    argument_template = """
        <s:%(name)s>%(value)s</s:%(name)s>"""
    method = 'post'

    def __init__(self, service_type, control_url, action_parameters):
        self.service_type = service_type
        self.control_url = control_url
        self.name = ''
        self.arguments = {}
        self.__dict__.update(action_parameters)

    @property
    def info(self):
        """
        Returns a list of tuples with the parameter-names, the according
        direction (in/out) and the data type of the action.
        """
        return [self.arguments[argument].info for argument in self.arguments]

    def _body_builder(self, kwargs):
        """
        Helper method to construct the appropriate SOAP-body to call a
        FritzBox-Service.
        """
        parameter = {
            'action_name': self.name,
            'service_type': self.service_type,
            'arguments': '',
            }
        if kwargs:
            arguments = [
                self.argument_template % {'name': k, 'value': v}
                for k, v in kwargs.items()
            ]
            parameter['arguments'] = ''.join(arguments)
        body = self.body_template.strip() % parameter
        return body

    def execute(self, **kwargs):
        """
        Calls the FritzBox action and returns a dictionary with the
        arguments. Raises an AuthorizationError in case a password is
        required for this request but is missing or wrong.
        """
        # self.address, self.port, self.password and self.user
        # are injected from the parser and FritzConnection as
        # action_parameters.
        # pylint: disable=no-member
        headers = self.header.copy()
        headers['soapaction'] = '%s#%s' % (self.service_type, self.name)
        data = self.envelope.strip() % self._body_builder(kwargs)
        url = 'http://%s:%s%s' % (self.address, self.port, self.control_url)
        auth = None
        if self.password:
            auth = HTTPDigestAuth(self.user, self.password)
        response = requests.post(url, data=data, headers=headers, auth=auth)
        if response.status_code == 401:
            # password required but missing or wrong
            raise AuthorizationError('unauthorized request')
        # lxml needs bytes, therefore response.content (not response.text)
        result = self.parse_response(response.content)
        return result

    def parse_response(self, response):
        """
        Evaluates the action-call response from a FritzBox.
        The response is a xml byte-string.
        Returns a dictionary with the received arguments-value pairs.
        The values are converted according to the given data_types.
        TODO: boolean and signed integers data-types from tr64 responses
        """
        result = {}
        root = etree.fromstring(response)
        for argument in self.arguments.values():
            try:
                value = root.find('.//%s' % argument.name).text
            except AttributeError:
                # will happen by searching for in-parameters and by
                # parsing responses with status_code != 200
                continue
            if argument.data_type.startswith('ui'):
                try:
                    value = int(value)
                except ValueError:
                    # should not happen
                    value = None
                except TypeError:
                    # raised in case that value is None. Should also not happen.
                    value = None
            result[argument.name] = value
        return result


class FritzActionArgument(object):
    """Attribute class for arguments."""
    # pylint: disable=too-few-public-methods
    name = ''
    direction = ''
    data_type = ''

    @property
    def info(self):
        """Returns all attributes as tuple"""
        return self.name, self.direction, self.data_type


class FritzService(object):
    """Attribute class for service."""
    # pylint: disable=too-few-public-methods

    def __init__(self, service_type, service_id, control_url, scpd_url):
        self.service_type = service_type
        self.service_id = service_id
        self.control_url = control_url
        self.scpd_url = scpd_url
        self.actions = {}

    @property
    def name(self):
        """Returns the servicename in a backward compatible way as:
        '<name>:<number>'
        """
        last_part = self.service_id.split(':')[-1]
        return ':'.join((last_part[:-1], last_part[-1]))


class FritzXmlParser(object):
    """Base class for parsing fritzbox-xml-files."""
    # pylint: disable=too-few-public-methods

    def __init__(self, address, port, filename=None):
        """Loads and parses an xml-file from a FritzBox."""
        if address is None:
            source = filename
        else:
            source = 'http://{0}:{1}/{2}'.format(address, port, filename)
        tree = etree.parse(source)
        self.root = tree.getroot()
        self.namespace = etree.QName(self.root.tag).namespace

    def nodename(self, name):
        """Extends name with the xmlns-prefix to a valid nodename."""
        return etree.QName(self.root, name)


class FritzDescParser(FritzXmlParser):
    """Class for parsing desc.xml-files."""

    def get_modelname(self):
        """Returns the FritzBox model name."""
        xpath = '%s/%s' % (self.nodename('device'), self.nodename('modelName'))
        return self.root.find(xpath).text

    def get_services(self):
        """Returns a list of FritzService-objects."""
        result = []
        nodes = self.root.iterfind(
            './/ns:service', namespaces={'ns': self.namespace})
        for node in nodes:
            result.append(FritzService(
                node.find(self.nodename('serviceType')).text,
                node.find(self.nodename('serviceId')).text,
                node.find(self.nodename('controlURL')).text,
                node.find(self.nodename('SCPDURL')).text))
        return result


class FritzSCDPParser(FritzXmlParser):
    """Class for parsing SCDP.xml-files"""

    def __init__(self, address, port, service, filename=None):
        """
        Reads and parses a SCDP.xml-file from FritzBox.
        'service' is a tuple of containing:
        (serviceType, controlURL, SCPDURL)
        'service' is a FritzService object:
        """
        self.state_variables = {}
        self.service = service
        if filename is None:
            # access the FritzBox
            super(FritzSCDPParser, self).__init__(address, port,
                                                  service.scpd_url)
        else:
            # for testing read the xml-data from a file
            super(FritzSCDPParser, self).__init__(None, None, filename=filename)

    def _read_state_variables(self):
        """
        Reads the stateVariable information from the xml-file.
        The information we like to extract are name and dataType so we
        can assign them later on to FritzActionArgument-instances.
        Returns a dictionary: key:value = name:dataType
        """
        nodes = self.root.iterfind(
            './/ns:stateVariable', namespaces={'ns': self.namespace})
        for node in nodes:
            key = node.find(self.nodename('name')).text
            value = node.find(self.nodename('dataType')).text
            self.state_variables[key] = value

    def get_actions(self, action_parameters):
        """Returns a list of FritzAction instances."""
        self._read_state_variables()
        actions = []
        nodes = self.root.iterfind(
            './/ns:action', namespaces={'ns': self.namespace})
        for node in nodes:
            action = FritzAction(self.service.service_type,
                                 self.service.control_url,
                                 action_parameters)
            action.name = node.find(self.nodename('name')).text
            action.arguments = self._get_arguments(node)
            actions.append(action)
        return actions

    def _get_arguments(self, action_node):
        """
        Returns a dictionary of arguments for the given action_node.
        """
        arguments = {}
        argument_nodes = action_node.iterfind(
            r'./ns:argumentList/ns:argument', namespaces={'ns': self.namespace})
        for argument_node in argument_nodes:
            argument = self._get_argument(argument_node)
            arguments[argument.name] = argument
        return arguments

    def _get_argument(self, argument_node):
        """
        Returns a FritzActionArgument instance for the given argument_node.
        """
        argument = FritzActionArgument()
        argument.name = argument_node.find(self.nodename('name')).text
        argument.direction = argument_node.find(self.nodename('direction')).text
        rsv = argument_node.find(self.nodename('relatedStateVariable')).text
        # track malformed xml-nodes? (i.e. misspelled)
        argument.data_type = self.state_variables.get(rsv, None)
        return argument


class FritzConnection(object):
    """
    FritzBox-Interface to read status-information and modify settings.
    """
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
        # The keys of the dictionary are becoming FritzAction instance
        # attributes on calling the FritzSCDPParser.get_actions() method
        # in self._read_services():
        self.action_parameters = {
            'address': address,
            'port': port,
            'user': user,
            'password': password
        }
        self.address = address
        self.port = port
        self.modelname = None
        self.services = {}
        self._read_descriptions(password)

    def __repr__(self):
        """
        Return a meaningful string if the instance gets printed or
        should represent itself.
        """
        return 'FritzConnection to model {} with ip {}'.format(
            self.modelname,
            self.address,
        )

    def _read_descriptions(self, password):
        """
        Read and evaluate the igddesc.xml file
        and the tr64desc.xml file if a password is given.
        """
        descfiles = [FRITZ_IGD_DESC_FILE]
        if password:
            descfiles.append(FRITZ_TR64_DESC_FILE)
        for descfile in descfiles:
            try:
                parser = FritzDescParser(self.address, self.port, descfile)
            except IOError:
                # failed to load a resource. Can happen on customized models
                # missing the igddesc.xml file.
                # It's save to ignore this error.
                continue
            if not self.modelname:
                self.modelname = parser.get_modelname()
            services = parser.get_services()
            self._read_services(services)

    def _read_services(self, services):
        """Get actions from services."""
        for service in services:
            parser = FritzSCDPParser(self.address, self.port, service)
            actions = parser.get_actions(self.action_parameters)
            service.actions = {action.name: action for action in actions}
            self.services[service.name] = service

    @property
    def actionnames(self):
        """
        Returns a alphabetical sorted list of tuples with all known
        service- and action-names.
        """
        actions = []
        for service_name in sorted(self.services.keys()):
            action_names = self.services[service_name].actions.keys()
            for action_name in sorted(action_names):
                actions.append((service_name, action_name))
        return actions

    def _get_action(self, service_name, action_name):
        """
        Returns an action-object (an instance of FritzAction) with the
        given action_name from the given service.
        Raises a ServiceError-Exeption in case of an unknown
        service_name and an ActionError in case of an unknown
        action_name.
        """
        try:
            service = self.services[service_name]
        except KeyError:
            raise ServiceError('Unknown Service: ' + service_name)
        try:
            action = service.actions[action_name]
        except KeyError:
            raise ActionError('Unknown Action: ' + action_name)
        return action

    def get_action_arguments(self, service_name, action_name):
        """
        Returns a list of tuples with all known arguments for the given
        service- and action-name combination. The tuples contain the
        argument-name, direction and data_type.
        """
        action = self._get_action(service_name, action_name)
        return action.info

    def call_action(self, service_name, action_name, **kwargs):
        """
        Executes the given action. Raise a KeyError on unkown actions.
        service_name can end with an identifier ':n' (with n as an
        integer) to differentiate between different services with the
        same name, like WLANConfiguration:1 or WLANConfiguration:2. In
        case the service_name does not end with an identifier the id
        ':1' will get added by default.
        """
        if ':' not in service_name:
            service_name += ':1'
        action = self._get_action(service_name, action_name)
        return action.execute(**kwargs)

    def reconnect(self):
        """
        Terminate the connection and reconnects with a new ip.
        Will raise a KeyError if this command is unknown (by any means).
        """
        self.call_action('WANIPConn', 'ForceTermination')


# ---------------------------------------------------------
# Inspection class for cli use:
# ---------------------------------------------------------

class FritzInspection(object):
    """
    Class for cli use to inspect available services and according
    actions of the given device (the Fritz!Box).
    """
    # pylint: disable=invalid-name  # self.fc is ok.

    def __init__(self,
                 address=FRITZ_IP_ADDRESS,
                 port=FRITZ_TCP_PORT,
                 user=FRITZ_USERNAME,
                 password=''):
        self.fc = FritzConnection(address, port, user, password)

    @staticmethod
    def _get_full_servicename(servicename):
        if ':' not in servicename:
            servicename += ':1'
        return servicename

    def get_servicenames(self):
        """Returns all known service names as alphabetically sorted list."""
        return sorted(self.fc.services.keys())

    def get_actionnames(self, servicename):
        """Returns a sorted list of the action names for the given service."""
        servicename = self._get_full_servicename(servicename)
        try:
            service = self.fc.services[servicename]
        except KeyError:
            return []
        return sorted(service.actions.keys())

    def view_header(self):
        """Send module version and Fritz!Box model name to stdout."""
        print('\nFritzConnection:')
        print('{:<20}{}'.format('version:', get_version()))
        print('{:<20}{}'.format('model:', self.fc.modelname))

    def view_servicenames(self):
        """Send all known service names to stdout."""
        print('Servicenames:')
        for name in self.get_servicenames():
            print('{:20}{}'.format('', name))

    def view_actionnames(self, servicename):
        """Send all action names of the given service to stdout."""
        print('\n{:<20}{}'.format('Servicename:', servicename))
        print('Actionnames:')
        for name in self.get_actionnames(servicename):
            print('{:20}{}'.format('', name))

    def view_actionarguments(self, servicename, actionname):
        """
        Send all action arguments of the given action and service to stdout.
        """
        servicename = self._get_full_servicename(servicename)
        print('\n{:<20}{}'.format('Servicename:', servicename))
        print('{:<20}{}'.format('Actionname:', actionname))
        print('Arguments:')
        self._view_arguments('{:20}{}', servicename, actionname)

    def view_servicearguments(self, servicename):
        """
        Send all action names and the corresponding parameters of the
        given service to stdout.
        """
        servicename = self._get_full_servicename(servicename)
        print('\n{:<20}{}'.format('Servicename:', servicename))
        actionnames = self.get_actionnames(servicename)
        for actionname in actionnames:
            print('{:<20}{}'.format('Actionname:', actionname))
            self._view_arguments('{:24}{}', servicename, actionname)

    def _view_arguments(self, fs, servicename, actionname):
        """Send all parameters for a given action and service to stdout."""
        for argument in sorted(
                self.fc.get_action_arguments(servicename, actionname)):
            print(fs.format('', argument))

    def view_complete(self):
        """Send the complete API of the device to stdout."""
        print('FritzBox API:')
        for servicename in self.get_servicenames():
            self.view_servicearguments(servicename)


# ---------------------------------------------------------
# terminal-output:
# ---------------------------------------------------------

def print_servicenames(address=FRITZ_IP_ADDRESS,
                       port=FRITZ_TCP_PORT,
                       user=FRITZ_USERNAME,
                       password=''):
    """Wrapper for FritzInspection to report all service names."""
    inspector = FritzInspection(address, port, user, password)
    inspector.view_header()
    inspector.view_servicenames()


def print_api(address=FRITZ_IP_ADDRESS,
              port=FRITZ_TCP_PORT,
              user=FRITZ_USERNAME,
              password=''):
    """Wrapper for FritzInspection to report the complete api."""
    inspector = FritzInspection(address, port, user, password)
    inspector.view_header()
    inspector.view_complete()


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def get_cli_arguments():
    """
    Returns a NameSpace object from the ArgumentParser parsing the given
    command line arguments.
    """
    parser = argparse.ArgumentParser(description='FritzBox API')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=None, const=None,
                        dest='address',
                        help='Specify ip-address of the FritzBox to connect to.'
                             'Default: %s' % FRITZ_IP_ADDRESS)
    parser.add_argument('--port',
                        nargs='?', default=None, const=None,
                        help='Port of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_TCP_PORT)
    parser.add_argument('-u', '--username',
                        nargs='?', default=os.getenv('FRITZ_USERNAME', None),
                        help='Fritzbox authentication username')
    parser.add_argument('-p', '--password',
                        nargs='?', default=os.getenv('FRITZ_PASSWORD', None),
                        help='Fritzbox authentication password')
    parser.add_argument('-r', '--reconnect',
                        action='store_true',
                        help='Reconnect and get a new ip')
    parser.add_argument('-s', '--services',
                        action='store_true',
                        help='List all available services')
    parser.add_argument('-S', '--serviceactions',
                        nargs=1,
                        help='List actions for the given service: <service>')
    parser.add_argument('-a', '--servicearguments',
                        nargs=1,
                        help='List arguments for the actions of a '
                             'specified service: <service>.')
    parser.add_argument('-A', '--actionarguments',
                        nargs=2,
                        help='List arguments for the given action of a '
                             'specified service: <service> <action>.')
    parser.add_argument('-c', '--complete',
                        action='store_true',
                        help='List all services with actionnames and arguments.'
                        )
    args = parser.parse_args()
    return args


def main():
    """CLI entry point."""
    args = get_cli_arguments()
    inspector = FritzInspection(
        args.address, args.port, args.username, args.password)
    inspector.view_header()
    if args.services:
        inspector.view_servicenames()
    elif args.serviceactions:
        inspector.view_actionnames(args.serviceactions[0])
    elif args.servicearguments:
        inspector.view_servicearguments(args.servicearguments[0])
    elif args.actionarguments:
        inspector.view_actionarguments(args.actionarguments[0],
                                       args.actionarguments[1])
    elif args.complete:
        inspector.view_complete()
    elif args.reconnect:
        inspector.fc.reconnect()
    print()  # print an empty line


if __name__ == '__main__':
    main()
