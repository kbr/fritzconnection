
from io import StringIO
from pathlib import Path

import pytest
from lxml import etree

from ..core.nodes import (
    SpecVersion,
    Service,
    ServiceList,
    Device,
    Description,

    AllowedValueList,
    AllowedValueRange,
    StateVariable,
    ServiceStateTable,
    Argument,
    ArgumentList,
    Action,
    ActionList,
    Scpd,
)


def parse_xml(source):
    tree = etree.parse(StringIO(source))
    root = tree.getroot()
    return root


IGDDESC_FILE = Path(__file__).parent/'xml'/'igddesc.xml'
IGDSCPD_FILE = Path(__file__).parent/'xml'/'igdconnSCPD.xml'


@pytest.fixture(scope="module")
def description():
    with open(IGDDESC_FILE) as fobj:
        root = parse_xml(fobj.read())
        return Description(root)

@pytest.fixture(scope="module")
def scpd():
    with open(IGDDESC_FILE) as fobj:
        root = parse_xml(fobj.read())
        return Scpd(root)


# --------------------------------------------------------
# test Description nodes
# --------------------------------------------------------

# Node: SpecVersion -----------------------------
spec_version_inp = parse_xml("""
    <specVersion>
        <major>1</major>
        <minor>0</minor>
    </specVersion>
""")

def test_SpecVersion_attributes(root=spec_version_inp):
    """test for instance attributes:"""
    sv = SpecVersion(root)
    assert sv.major == '1'
    assert sv.minor == '0'

def test_SpecVersion_version(root=spec_version_inp):
    """test version attribute"""
    sv = SpecVersion(root)
    assert sv.version == '1.0'


# Node: Service ---------------------------------
service_inp = parse_xml("""
    <service>
        <serviceType>urn:schemas-upnp-org:service:WANIPConnection:1</serviceType>
        <serviceId>urn:upnp-org:serviceId:WANIPConn1</serviceId>
        <controlURL>/igdupnp/control/WANIPConn1</controlURL>
        <eventSubURL>/igdupnp/control/WANIPConn1</eventSubURL>
        <SCPDURL>/igdconnSCPD.xml</SCPDURL>
    </service>
""")

@pytest.mark.parametrize(
    "root, name, value", [
        (service_inp, 'serviceType', 'urn:schemas-upnp-org:service:WANIPConnection:1'),
        (service_inp, 'serviceId', 'urn:upnp-org:serviceId:WANIPConn1'),
        (service_inp, 'controlURL', '/igdupnp/control/WANIPConn1'),
        (service_inp, 'eventSubURL', '/igdupnp/control/WANIPConn1'),
        (service_inp, 'SCPDURL', '/igdconnSCPD.xml'),
    ]
)
def test_Service_attributes(root, name, value):
    """check for all atributes"""
    s = Service(root)
    assert getattr(s, name) == value

def test_Service_name(root=service_inp):
    """check for service name."""
    s = Service(root)
    assert s.name == 'WANIPConn1'


# Node: ServiceList -----------------------------
service_list_inp = parse_xml("""
    <serviceList>
        <service>
            <serviceType>urn:schemas-upnp-org:service:WANDSLLinkConfig:1</serviceType>
            <serviceId>urn:upnp-org:serviceId:WANDSLLinkC1</serviceId>
            <controlURL>/igdupnp/control/WANDSLLinkC1</controlURL>
            <eventSubURL>/igdupnp/control/WANDSLLinkC1</eventSubURL>
            <SCPDURL>/igddslSCPD.xml</SCPDURL>
        </service>
        <service>
            <serviceType>urn:schemas-upnp-org:service:WANIPConnection:1</serviceType>
            <serviceId>urn:upnp-org:serviceId:WANIPConn1</serviceId>
            <controlURL>/igdupnp/control/WANIPConn1</controlURL>
            <eventSubURL>/igdupnp/control/WANIPConn1</eventSubURL>
            <SCPDURL>/igdconnSCPD.xml</SCPDURL>
        </service>
        <service>
            <serviceType>urn:schemas-upnp-org:service:WANIPv6FirewallControl:1</serviceType>
            <serviceId>urn:upnp-org:serviceId:WANIPv6Firewall1</serviceId>
            <controlURL>/igd2upnp/control/WANIPv6Firewall1</controlURL>
            <eventSubURL>/igd2upnp/control/WANIPv6Firewall1</eventSubURL>
            <SCPDURL>/igd2ipv6fwcSCPD.xml</SCPDURL>
        </service>
    </serviceList>
""")

def test_ServiceList_len(root=service_list_inp):
    """test if all services are scanned."""
    s = ServiceList(root)
    assert len(s) == 3


def test_ServiceList_iterate(root=service_list_inp):
    """test if all services are scanned."""
    s = ServiceList(root)
    items = len(s)
    for n, service in enumerate(s, 1):
        pass
    assert n == items


# Node: Device ----------------------------------
device_short_inp = parse_xml("""
    <device>
        <deviceType>urn:schemas-upnp-org:device:InternetGatewayDevice:1</deviceType>
        <friendlyName>FRITZ!Box 7590</friendlyName>
        <manufacturer>AVM Berlin</manufacturer>
        <manufacturerURL>http://www.avm.de</manufacturerURL>
        <modelDescription>FRITZ!Box 7590</modelDescription>
        <modelName>FRITZ!Box 7590</modelName>
        <modelNumber>avm</modelNumber>
        <modelURL>http://www.avm.de</modelURL>
        <UDN>uuid:75802409-bccb-40e7-8e6c-989BCB2B93B0</UDN>
    </device>
""")

def test_Device_uuid(root=device_short_inp):
    """test for attribute access."""
    d = Device(root)
    assert d.uuid == '75802409-bccb-40e7-8e6c-989BCB2B93B0'


def test_Device_model_name(root=device_short_inp):
    """test for attribute access."""
    d = Device(root)
    assert d.model_name == 'FRITZ!Box 7590'


# Node: Description -----------------------------

def test_Description_namespace(description):
    """test for main device name"""
    assert description.namespace == 'urn:schemas-upnp-org:device-1-0'

def test_Description_spec_version(description):
    """test for specVersion"""
    assert description.spec_version == '1.0'

def test_Description_device_name(description):
    """test for main device name"""
    assert description.device_model_name == 'FRITZ!Box 7590'

def test_Description_service_num(description):
    """check service collection."""
    assert len(description.services) == 5

@pytest.mark.parametrize(
    "name", [
        'any1',
        'WANCommonIFC1',
        'WANDSLLinkC1',
        'WANIPConn1',
        'WANIPv6Firewall1'
    ]
)
def test_Description_service_names(name, description):
    """check whether the description can find its services."""
    service = description.services[name]
    assert service.name == name


# Node: AllowedValueList ------------------------

allowed_value_list_inp = parse_xml("""
    <allowedValueList>
        <allowedValue>Unconfigured</allowedValue>
        <allowedValue>IP_Routed</allowedValue>
        <allowedValue>IP_Bridged</allowedValue>
    </allowedValueList>
""")

def test_AllowedValueList_has_property(root=allowed_value_list_inp):
    """check whether the allowedValues are stored"""
    avl = AllowedValueList(root)
    assert isinstance(avl.values, list) is True

def test_AllowedValue_has_length(root=allowed_value_list_inp):
    """Instance has length like a list"""
    avl = AllowedValueList(root)
    print(avl.values)
    assert len(avl.values) == 3

@pytest.mark.parametrize(
    "root, value", [
        (allowed_value_list_inp, 'Unconfigured'),
        (allowed_value_list_inp, 'IP_Routed'),
        (allowed_value_list_inp, 'IP_Bridged'),
    ]
)
def test_AllowedValue_content(root, value):
    """check content of allowed values"""
    avl = AllowedValueList(root)
    assert value in avl.values


# Node: AllowedValueRange -----------------------
state_variable_inp = parse_xml("""
    <allowedValueRange>
        <minimum>0</minimum>
        <maximum>4294967295</maximum>
        <step>1</step>
    </allowedValueRange>
""")

def test_AllowedValueRange_attributes(root=state_variable_inp):
    """check attributes"""
    avr = AllowedValueRange(root)
    assert avr.minimum == '0'
    assert avr.maximum == '4294967295'
    assert avr.step == '1'


# Node: StateVariable ---------------------------
state_variable_inp = parse_xml("""
    <stateVariable sendEvents="no">
        <name>NATEnabled</name>
        <dataType>boolean</dataType>
        <defaultValue>1</defaultValue>
    </stateVariable>
""")

def test_StateVariable_attributes(root=state_variable_inp):
    """check attributes"""
    sv = StateVariable(root)
    assert sv.name == 'NATEnabled'
    assert sv.dataType == 'boolean'
    assert sv.defaultValue == '1'

def test_StateVariable_tag_attributes(root=state_variable_inp):
    """check for tag attributes"""
    sv = StateVariable(root)
    assert hasattr(sv, 'tag_attributes')

def test_StateVariable_tag_attribute_value(root=state_variable_inp):
    """check for tag attributes"""
    sv = StateVariable(root)
    assert sv.tag_attributes['sendEvents'] == 'no'


# Node: ServiceStateTable -----------------------
service_state_table_inp = parse_xml("""
    <serviceStateTable>
        <stateVariable sendEvents="no">
            <name>ConnectionType</name>
            <dataType>string</dataType>
            <defaultValue>Unconfigured</defaultValue>
        </stateVariable>
        <stateVariable sendEvents="yes">
            <name>PossibleConnectionTypes</name>
            <dataType>string</dataType>
            <allowedValueList>
            <allowedValue>Unconfigured</allowedValue>
            <allowedValue>IP_Routed</allowedValue>
            <allowedValue>IP_Bridged</allowedValue>
            </allowedValueList>
        </stateVariable>
    </serviceStateTable>
""")

def test_ServicStateTable_len(root=service_state_table_inp):
    """check len of table"""
    sst = ServiceStateTable(root)
    assert len(sst) == 2

def test_ServicStateTable_iterable(root=service_state_table_inp):
    """test whether the ServiceStateTable is an iterable."""
    sst = ServiceStateTable(root)
    items = len(sst)
    for n, entry in enumerate(sst, 1):
        pass
    assert n == items

@pytest.mark.parametrize(
    "root, name", [
        (service_state_table_inp, 'ConnectionType'),
        (service_state_table_inp, 'PossibleConnectionTypes'),
    ]
)
def test_ServiceStateTable_get_sv(root, name):
    """Test access of StateVariables by name"""
    sst = ServiceStateTable(root)
    # should work without KeyErrors:
    sv = sst.state_variables[name]
    assert sv.name == name

# Node: Argument --------------------------------
argument_inp = parse_xml("""
    <argument>
        <name>NewConnectionType</name>
        <direction>out</direction>
        <relatedStateVariable>ConnectionType</relatedStateVariable>
    </argument>
""")

@pytest.mark.parametrize(
    "root, attribute, value", [
        (argument_inp, 'name', 'NewConnectionType'),
        (argument_inp, 'direction', 'out'),
        (argument_inp, 'relatedStateVariable', 'ConnectionType'),
    ]
)
def test_Argument(root, attribute, value):
    """test for attributes."""
    arg = Argument(root)
    attr = getattr(arg, attribute)
    assert attr == value


# Node: ArgumentList ----------------------------
argument_list_inp = parse_xml("""
    <argumentList>
        <argument>
            <name>NewConnectionType</name>
            <direction>out</direction>
            <relatedStateVariable>ConnectionType</relatedStateVariable>
        </argument>
        <argument>
            <name>NewPossibleConnectionTypes</name>
            <direction>out</direction>
            <relatedStateVariable>PossibleConnectionTypes</relatedStateVariable>
        </argument>
    </argumentList>
""")

def test_ArgumentList_len(root=argument_list_inp):
    """check for number of arguments"""
    al = ArgumentList(root)
    assert len(al) == 2

def test_ArgumentList_iter(root=argument_list_inp):
    """Test that ArgumentList is an iterable."""
    al = ArgumentList(root)
    items = len(al)
    for n, _ in enumerate(al, 1):
        pass
    assert items == n


# Node: Action ----------------------------------
action_inp = parse_xml("""
<action>
    <name>GetConnectionTypeInfo</name>
    <argumentList>
        <argument>
            <name>NewConnectionType</name>
            <direction>out</direction>
            <relatedStateVariable>ConnectionType</relatedStateVariable>
        </argument>
        <argument>
            <name>NewPossibleConnectionTypes</name>
            <direction>out</direction>
            <relatedStateVariable>PossibleConnectionTypes</relatedStateVariable>
        </argument>
    </argumentList>
</action>
""")

def test_Action_name(root=action_inp):
    """test for Action attribute 'name'"""
    ac = Action(root)
    assert ac.name == 'GetConnectionTypeInfo'

def test_Action_arguments(root=action_inp):
    """test that the Action has an 'arguments' attribute with two items."""
    ac = Action(root)
    assert len(ac.arguments) == 2

@pytest.mark.parametrize(
    "root, name", [
        (action_inp, 'NewConnectionType'),
        (action_inp, 'NewPossibleConnectionTypes'),
    ]
)
def test_Action_arguments_by_name(root, name):
    """test that the Action has an 'arguments' attribute with two items."""
    ac = Action(root)
    argument = ac.arguments[name]
    assert argument.name == name


# Node: ActionList ------------------------------
action_list_inp = parse_xml("""
    <actionList>
        <action>
            <name>SetConnectionType</name>
            <argumentList>
                <argument>
                <name>NewConnectionType</name>
                <direction>in</direction>
                <relatedStateVariable>ConnectionType</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
        <action>
            <name>GetConnectionTypeInfo</name>
            <argumentList>
                <argument>
                    <name>NewConnectionType</name>
                    <direction>out</direction>
                    <relatedStateVariable>ConnectionType</relatedStateVariable>
                </argument>
                <argument>
                    <name>NewPossibleConnectionTypes</name>
                    <direction>out</direction>
                    <relatedStateVariable>PossibleConnectionTypes</relatedStateVariable>
                </argument>
            </argumentList>
        </action>
    </actionList>
""")

def test_ActionList_len(root=action_list_inp):
    """test that ActionList is a sequence with a len."""
    al = ActionList(root)
    assert len(al) == 2


def test_ActionList_iter(root=action_list_inp):
    """test that ActionList is an iterable."""
    al = ActionList(root)
    items = len(al)
    for n, _ in enumerate(al, 1):
        pass
    assert items == n

