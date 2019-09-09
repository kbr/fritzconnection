#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test.py

unittests for fritzconnection

The xml-test-content is loaded from files because we need well defined
values which may vary by different AVM FritzBox models.
"""

import os.path
import unittest

from fritzconnection import (
    FritzXmlParser,
    FritzDescParser,
    FritzSCDPParser,
    FritzAction,
    FritzActionArgument,
    FritzService,
    )

FRITZBOX_MODEL = 'FRITZ!Box Fon WLAN 7170'
DESCRIPTION_FILE = os.path.join(os.path.dirname(__file__),
                                'test_xml', 'igddesc.xml')
SCPD_FILE = os.path.join(os.path.dirname(__file__),
                         'test_xml', 'igdconnSCPD.xml')


class TestFritzXmlParser(unittest.TestCase):

    def setUp(self):
        self.fp = FritzXmlParser(None, None, filename=DESCRIPTION_FILE)
        self.namespace = 'urn:schemas-upnp-org:device-1-0'

    def test_namespace(self):
        self.assertEqual(self.namespace, self.fp.namespace)

    def test_nodename(self):
        self.assertEqual('{%s}%s' % (self.namespace, 'mynode'),
                          self.fp.nodename('mynode'))


class TestFritzDescParser(unittest.TestCase):

    def setUp(self):
        self.fp = FritzDescParser(None, None, filename=DESCRIPTION_FILE)

    def test_modelname(self):
        self.assertEqual(FRITZBOX_MODEL, self.fp.get_modelname())

    def test_getservices(self):
        """
        We get a list of services. Instead of comparing the entire list
        we look at the last item of the first tuple in the list, which
        should be '/any.xml'. If this test passes we assume that this is
        the case for all tuples in the list.
        """
        services = self.fp.get_services()
        self.assertEqual(r'/any.xml', services[0].scpd_url)


class FritzSCDPTestParser(FritzSCDPParser):
    """Helper subclass of FritzSCDPParser to generate an object configured
       for testing purposes
    """

    def __init__(self, *args, **kwargs):
        self.service = FritzService(
                    'urn:schemas-upnp-org:service:WANCommonInterfaceConfig:1',
                    'urn:upnp-org:serviceId:WANCommonIFC1',
                    '/upnp/control/WANCommonIFC1',
                    '/igdicfgSCPD.xml'
                    )
        super(FritzSCDPTestParser, self).__init__(None, None, self.service, filename=SCPD_FILE)


class TestFritzSCDPParser(unittest.TestCase):

    def setUp(self):
        self.fp = FritzSCDPTestParser()

    def test_get_service_name(self):
        self.assertEqual('WANCommonIFC:1', self.fp.service.name)

    def test_read_state_variables(self):
        """Parse the stateVariables and check for a single value."""
        self.fp._read_state_variables()
        self.assertEqual(
            'string', self.fp.state_variables.get('ExternalIPAddress'))

    def test_get_actions(self):
        """Read actionnames and corresponding arguments from xml-file."""
        actions = self.fp.get_actions({})
        first_action = actions[0]
        self.assertEqual(
            type(FritzAction(None, None, {})), type(first_action))


class TestFritzAction(unittest.TestCase):
    """Test for response parsing."""

    # The action we use for testing:
    action_name = 'GetStatusInfo'

    # service_type for simulated call_action('GetStatusInfo'):
    service_type = 'urn:schemas-upnp-org:service:WANIPConnection:1'

    # the control_url for this action (for object initialisation)
    control_url = '/upnp/control/WANIPConn1'

    # typical response as given by call_action('GetStatusInfo'):
    response = b'<?xml version="1.0" encoding="utf-8"?>\n<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">\n<s:Body>\n<u:GetStatusInfoResponse xmlns:u="urn:schemas-upnp-org:service:WANIPConnection:1">\n<NewConnectionStatus>Connected</NewConnectionStatus>\n<NewLastConnectionError>ERROR_NONE</NewLastConnectionError>\n<NewUptime>29938</NewUptime>\n</u:GetStatusInfoResponse>\n</s:Body>\n</s:Envelope>'

    def get_arguments(self):
        """
        We need the 'GetStatusInfo' arguments for parsing the response.
        So we extract them here. Because this is code tested before this
        function gets called, we know it works.
        Returns a dictionary with argumentname,
        FritzActionArgument-object pairs.
        """
        scdp = FritzSCDPTestParser()
        actions = {action.name: action for action in scdp.get_actions({})}
        return actions[self.action_name].arguments

    def test_parse_response(self):
        fa = FritzAction(self.service_type, self.control_url, {})
        fa.arguments = self.get_arguments()  # argument-injection
        result = fa.parse_response(self.response)
        self.assertEqual('Connected', result['NewConnectionStatus'])
        self.assertEqual('ERROR_NONE', result['NewLastConnectionError'])
        self.assertEqual(29938,  result['NewUptime'])


if __name__ == '__main__':
    unittest.main()
