#! /opt/local/bin/python2.7
#! /usr/bin/env python2.7

"""
fritzconnection.py

This is a tool to communicate with the FritzBox.
All availabel actions (aka commands) and corresponding parameters are
read from the xml-configuration files requested from the FritzBox. So
the available actions may change depending on the FritzBox model and
firmware.

Runs with python >= 2.7
"""

try:
    # python 3
    from http.client import HTTPConnection
    from urllib.request import urlopen
except ImportError:
    # python 2
    from httplib import HTTPConnection
    from urllib2 import urlopen
import xml.etree.ElementTree as etree
import xml.sax


# FritzConnection defaults:
FRITZ_ADDRESS = '169.254.1.1'
FRITZ_TCP_PORT = 49000
FRITZ_DESC_FILES = ('igddesc.xml',)# 'tr64desc.xml')


class FritzBoxSAXHandler(xml.sax.handler.ContentHandler):
    """
    Handler for xml-response returned from FritzBox.
    """

    def __init__(self, arguments, *args, **kwargs):
        # for old-style class compatibility we don't use super:
        xml.sax.handler.ContentHandler.__init__(self, *args, **kwargs)
        self.argument = None
        self.arguments = arguments
        self.values = {argument: '' for argument in arguments}

    def startElement(self, name, attrs):
        if name in self.values:
            self.argument = name

    def endElement(self, name):
        if name == self.argument:
            self.argument = None

    def characters(self, content):
        if self.argument:
            self.values[self.argument] = content

    def get_values(self):
        for argument, value in self.values.items():
            data_type = self.arguments[argument].data_type
            if data_type.startswith('ui'):
                try:
                    self.values[argument] = int(value)
                except ValueError:
                    # should not happen, but happens :(
                    self.values[argument] = 0
        return self.values


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
    address = FRITZ_ADDRESS
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

    def execute(self, timeout=2):
        """
        Calls the FritzBox action and returns a dictionary with the arguments.
        TODO: set values!
        Will raise an IOError if connection.request() fails.
        """
        header = self.header.copy()
        header['soapaction'] = '%s#%s' % (self.service_type, self.name)
        message = self.envelope % (self.name, self.service_type)
        connection = HTTPConnection(self.address, self.port, timeout)
        connection.request(self.method, self.control_url, message, header)
        response = connection.getresponse().read()
        handler = FritzBoxSAXHandler(self.arguments)
        xml.sax.parseString(response, handler)
        return handler.get_values()


class FritzActionArgument(object):
    """Attribute class for arguments."""
    name = ''
    direction = ''
    data_type = ''

    @property
    def info(self):
        return (self.name, self.direction, self.data_type)


class FritzXmlParser(object):
    """
    Base class for parsing fritzbox-xml-files.
    """

    def __init__(self, address, port, filename):
        """Loads and parses an xml-file from a FritzBox."""
        stream = urlopen('http://%s:%s/%s' % (address, port, filename))
        content = stream.read()
        self.root = etree.fromstring(content)
        self.ns_prefix = ''
        if self.root.tag.startswith('{'):
            self.ns_prefix = self.root.tag.split('}')[0] + '}'

    def nodename(self, name):
        """Extends name with the xmlns-prefix to a valid nodename."""
        return "%s%s" % (self.ns_prefix, name)


class FritzDescParser(FritzXmlParser):
    """Class for parsing desc.xml-files."""

    def get_modelname(self):
        """Returns the FritzBox model name."""
        xpath = "%sdevice/%smodelName" % (self.ns_prefix, self.ns_prefix)
        return self.root.find(xpath).text

    def get_services(self):
        """
        Returns a list of tuples with service informations:
        (serviceType, controlURL, SCDPURL)
        """
        result = []
        nodes = self.root.iter(self.nodename('service'))
        for node in nodes:
            result.append((
                node.find(self.nodename('serviceType')).text,
                node.find(self.nodename('controlURL')).text,
                node.find(self.nodename('SCPDURL')).text))
        return result


class FritzSCDPParser(FritzXmlParser):
    """Class for parsing SCDP.xml-files"""

    def __init__(self, address, port, service):
        """
        Reads and parses a SCDP.xml-file from FritzBox.
        'service' is a tuple of containing:
        (serviceType, controlURL, SCPDURL)
        """
        self.service_type, self.control_url, scpd_url = service
        super(FritzSCDPParser, self).__init__(address, port, scpd_url)
        self.state_variables = self._get_state_variables()

    def _get_state_variables(self):
        """
        Reads the stateVariable information from the xml-file.
        The information we like to extract are name and dataType so we
        can assign them later on to FritzActionArgument-instances.
        Returns a dictionary: key:value = name:dataType
        """
        state_variables = {}
        nodes = self.root.iter(self.nodename('stateVariable'))
        for node in nodes:
            key = node.find(self.nodename('name')).text
            value = node.find(self.nodename('dataType')).text
            state_variables[key] = value
        return state_variables

    def get_actions(self):
        """Returns a list of FritzAction instances."""
        actions = []
        nodes = self.root.iter(self.nodename('action'))
        for node in nodes:
            action = FritzAction(self.service_type, self.control_url)
            action.name = node.find(self.nodename('name')).text
            action.arguments = self._get_arguments(node)
            actions.append(action)
        return actions

    def _get_arguments(self, action_node):
        """
        Returns a dictionary of arguments for the given action_node.
        """
        arguments = {}
        xpath = r'./%s/%s' % (self.nodename('argumentList'),
                              self.nodename('argument'))
        argument_nodes = action_node.findall(xpath)
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
    def __init__(self, address=FRITZ_ADDRESS,
                       port=FRITZ_TCP_PORT,
                       descfiles=FRITZ_DESC_FILES):
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


if __name__ == '__main__':
    print('FritzConnection:')
    fc = FritzConnection()

    print(fc.modelname)
    print(fc.actionnames)
    print(fc.get_action_arguments('GetStatusInfo'))
    print(fc.call_action('GetStatusInfo'))
    print(fc.call_action('GetTotalBytesSent'))
    print(fc.call_action('GetTotalBytesReceived'))
    print(fc.call_action('GetExternalIPAddress'))
    print(fc.call_action('GetCommonLinkProperties'))
#     print(fc.call_action('ForceTermination'))
