# -*- coding: utf-8 -*-

"""
fritzconnection.py

This is a tool to communicate with the FritzBox.
All availabel actions (aka commands) and corresponding parameters are
read from the xml-configuration files requested from the FritzBox. So
the available actions may change depending on the FritzBox model and
firmware.
The command-line interface allows the api-inspection.

#Runs with python >= 2.7 # TODO: test with 2.7
"""

_version_ = '0.2.0'

import argparse
import requests

from lxml import etree


# FritzConnection defaults:
FRITZ_IP_ADDRESS = '169.254.1.1'
FRITZ_TCP_PORT = 49000
FRITZ_DESC_FILES = ('igddesc.xml',)# 'tr64desc.xml')


# version-access:
def get_version():
    return _version_


class FritzAction(object):
    """
    Class representing an action (aka command).
    Knows how to execute itself.
    """
    header = {'soapaction': '',
              'content-type': 'text/xml',
              'charset': 'utf-8'}
    envelope = """
        <?xml version="1.0" encoding="utf-8"?>
        <s:Envelope s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"
                    xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">
        <s:Body>
        <u:%s xmlns:u="%s" />
        </s:Body>
        </s:Envelope>
        """
    address = FRITZ_IP_ADDRESS
    port = FRITZ_TCP_PORT
    method = 'post'

    def __init__(self, service_type, control_url):
        self.service_type = service_type
        self.control_url = control_url
        self.name = ''
        self.arguments = {}

    @property
    def info(self):
        return [self.arguments[argument].info for argument in self.arguments]

    def execute(self):
        """
        Calls the FritzBox action and returns a dictionary with the arguments.
        TODO: send arguments in case of tr64-connection.
        """
        headers = self.header.copy()
        headers['soapaction'] = '%s#%s' % (self.service_type, self.name)
        data = self.envelope % (self.name, self.service_type)
        url = 'http://%s:%s%s' % (self.address, self.port, self.control_url)
        response = requests.post(url, data=data, headers=headers)
        # lxml needs bytes, therefor .content (not .text)
        result = self.parse_response(response.content)
        return result

    def parse_response(self, response):
        """
        Evaluates the action-call response from a FritzBox.
        The response is a xml byte-string.
        Returns a dictionary with the received arguments-value pairs.
        The values are converted according to the given data_types.
        """
        result = {}
        root = etree.fromstring(response)
        for argument in self.arguments.values():
            value = root.find('.//%s' % argument.name).text
            if argument.data_type.startswith('ui'):
                try:
                    value = int(value)
                except ValueError:
                    # should not happen
                    value = None
            result[argument.name] = value
        return result


class FritzActionArgument(object):
    """Attribute class for arguments."""
    name = ''
    direction = ''
    data_type = ''

    @property
    def info(self):
        return (self.name, self.direction, self.data_type)


class FritzXmlParser(object):
    """Base class for parsing fritzbox-xml-files."""

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
        """
        Returns a list of tuples with service informations:
        (serviceType, controlURL, SCDPURL)
        """
        result = []
        nodes = self.root.iterfind(
            './/ns:service', namespaces={'ns': self.namespace})
        for node in nodes:
            result.append((
                node.find(self.nodename('serviceType')).text,
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
        """
        self.state_variables = {}
        self.service_type, self.control_url, scpd_url = service
        if filename is None:
            # access the FritzBox
            super(FritzSCDPParser, self).__init__(address, port, scpd_url)
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

    def get_actions(self):
        """Returns a list of FritzAction instances."""
        self._read_state_variables()
        actions = []
        nodes = self.root.iterfind(
            './/ns:action', namespaces={'ns': self.namespace})
        for node in nodes:
            action = FritzAction(self.service_type,
                                 self.control_url)
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
        argument.data_type = self.state_variables[rsv]
        return argument


class FritzConnection(object):
    """
    FritzBox-Interface for status-information
    """
    def __init__(self, address=FRITZ_IP_ADDRESS,
                       port=FRITZ_TCP_PORT,
                       descfiles=FRITZ_DESC_FILES,
                       user='',
                       password=''):
        FritzAction.address = address
        FritzAction.port = port
        self.address = address
        self.port = port
        self.descfiles = descfiles
        self.modelname = None
        self.actions = {}
        self._read_descriptions()

    def _read_descriptions(self):
        """Read and evaluate FRITZ_DESC_FILES."""
        for descfile in self.descfiles:
            parser = FritzDescParser(self.address, self.port, descfile)
            if not self.modelname:
                self.modelname = parser.get_modelname()
            services = parser.get_services()
            self._read_services(services)

    def _read_services(self, services):
        """Get actions from services."""
        for service in services:
            parser = FritzSCDPParser(self.address, self.port, service)
            actions = parser.get_actions()
            self.actions.update({action.name: action for action in actions})

    @property
    def actionnames(self):
        """Returns a alphabetical sorted list with all known action-names."""
        return sorted(self.actions.keys())

    def get_action_arguments(self, action_name):
        """
        Returns a list of tuples with all known arguments for the given
        action-name. The tuples contain the argument-name, direction and
        data_type.
        'action_name' is a string and must be a member of the actions
        returned by 'actionsnames'. An unknown action_name will raise a
        KeyError.
        """
        return self.actions[action_name].info

    def call_action(self, action_name):
        """Executes the given action. Raise a KeyError on unkown actions."""
        return self.actions[action_name].execute()

    def reconnect(self):
        """
        Terminate the connection and reconnects with a new ip.
        Will raise a KeyError if this command is unknown (by any means).
        """
        self.call_action('ForceTermination')


# ---------------------------------------------------------
# cli-section:
# ---------------------------------------------------------

def _get_cli_arguments():
    parser = argparse.ArgumentParser(description='FritzBox API')
    parser.add_argument('-i', '--ip-address',
                        nargs='?', default=FRITZ_IP_ADDRESS,
                        dest='address',
                        help='ip-address of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_IP_ADDRESS)
    parser.add_argument('-p', '--port',
                        nargs='?', default=FRITZ_TCP_PORT,
                        dest='port',
                        help='port of the FritzBox to connect to. '
                             'Default: %s' % FRITZ_TCP_PORT)
    parser.add_argument('-a', '--actionnames',
                        action='store_true',
                        dest='show_actionnames',
                        help='show supported actionnames')
    parser.add_argument('-l', '--list-args',
                        nargs=1,
                        dest='show_action_arg',
                        help='show arguments of a given action: -l <actionname>')
    parser.add_argument('-c', '--complete-args',
                        action='store_true',
                        dest='show_all_action_args',
                        help='show arguments of all actions')
    parser.add_argument('-r', '--reconnect',
                        action='store_true',
                        dest='reconnect',
                        help='reconnect with new ip')
    args = parser.parse_args()
    return args

def _print_actionnames(fc):
    print('{:<20}'.format('actionnames:'))
    for name in fc.actionnames:
        print('{:<20}{}'.format('', name))

def _print_action_arg(fc, actionname):
    args = fc.get_action_arguments(actionname)
    print('\n{:<20}{}'.format('actionname:', actionname))
    print('{:<20}'.format('arguments:'))
    for arg in args:
        print('{:<20}{}'.format('', arg))

def _print_all_action_args(fc):
    for name in fc.actionnames:
        _print_action_arg(fc, name)

def _print_information(arguments):
    print('\nFritzConnection:')
    print('{:<20}{}'.format('version:', get_version()))
    fc = FritzConnection(address=arguments.address, port=arguments.port)
    print('{:<20}{}'.format('model:', fc.modelname))
    if arguments.show_actionnames:
        _print_actionnames(fc)
    if arguments.show_action_arg:
        _print_action_arg(fc, arguments.show_action_arg[0])
    if arguments.show_all_action_args:
        _print_all_action_args(fc)
    if arguments.reconnect:
        fc.reconnect()

if __name__ == '__main__':
    _print_information(_get_cli_arguments())
