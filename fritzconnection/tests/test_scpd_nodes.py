"""
Tests for parsing the device description files like

    igdconnSCPD.xml

"""

from io import StringIO
from pathlib import Path

import pytest

from lxml import etree
#import xml.etree.ElementTree as etree  # like lxml
import pytest


IGDDESC_FILE = Path(__file__).parent / 'xml' / 'igdconnSCPD.xml'


from ..core.fritzconnection import (
    SpecVersion,
    AllowedValueList,
    AllowedValueRange,
    StateVariable,
    Argument,
    ArgumentList,
    Action,
)


def parse_xml(source):
    tree = etree.parse(StringIO(source))
    root = tree.getroot()
    return root


# --------------------------------------------------------
# test SCPD nodes
# --------------------------------------------------------

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


state_variable_min_inp = parse_xml("""
    <stateVariable sendEvents="yes">
        <name>ExternalIPAddress</name>
        <dataType>string</dataType>
    </stateVariable>
""")

def test_StateVariable_attribute_access(root=state_variable_min_inp):
    """access defined and undefined attributes, because some are optional.
    """
    sv = StateVariable(root)
    assert sv.name == 'ExternalIPAddress'
    assert sv.type == 'string'
    assert sv.default == None
    assert isinstance(sv.allowed_values, list)
    assert sv.allowed_value_range is None


state_variable_max_inp = parse_xml("""
    <stateVariable sendEvents="no">
        <name>Uptime</name>
        <dataType>ui4</dataType>
        <defaultValue>0</defaultValue>
        <allowedValueRange>
            <minimum>0</minimum>
            <maximum>4294967295</maximum>
            <step>1</step>
        </allowedValueRange>
    </stateVariable>
""")

def test_StateVariable_nested_attribute_access(root=state_variable_max_inp):
    """access optinal defined attributes."""
    sv = StateVariable(root)
    assert sv.name == 'Uptime'
    assert sv.type == 'ui4'
    assert sv.default == '0'
    vr = sv.allowed_value_range
    assert isinstance(vr, dict)


argument_inp = parse_xml("""
    <argument>
        <name>NewConnectionType</name>
        <direction>out</direction>
        <relatedStateVariable>ConnectionType</relatedStateVariable>
    </argument>
""")

def test_Argument_inp(root=argument_inp):
    """test accessing all attributes."""
    arg = Argument(root)
    assert arg.name == 'NewConnectionType'
    assert arg.direction == 'out'
    assert arg.relatedStateVariable == 'ConnectionType'
    # and test the convenience property:
    assert arg.state_variable_name == 'ConnectionType'


argument_list_inp = parse_xml("""
    <argumentList>
        <argument>
            <name>NewConnectionStatus</name>
            <direction>out</direction>
            <relatedStateVariable>ConnectionStatus</relatedStateVariable>
        </argument>
        <argument>
            <name>NewLastConnectionError</name>
            <direction>out</direction>
            <relatedStateVariable>LastConnectionError</relatedStateVariable>
        </argument>
        <argument>
            <name>NewUptime</name>
            <direction>out</direction>
            <relatedStateVariable>Uptime</relatedStateVariable>
        </argument>
    </argumentList>
""")

def test_ArgumentList_len(root=argument_list_inp):
    """test for number of entries."""
    al = ArgumentList(root)
    assert len(al) == 3

def test_ArgumentList_iterate(root=argument_list_inp):
    """ArgumentList should be an iterable returning Arguments."""
    al = ArgumentList(root)
    for arg in al:
        assert isinstance(arg, Argument)


action_full_input = parse_xml("""
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

def test_Action_with_arguments(root=action_full_input):
    """check for arguments."""
    ac = Action(root)
    assert ac.name == 'GetConnectionTypeInfo'
    assert isinstance(ac.argumentList, list)

@pytest.mark.parametrize(
    "root, name", [
        (action_full_input, 'NewConnectionType'),
        (action_full_input, 'NewPossibleConnectionTypes'),
    ]
)
def test_Action_argument_access(root, name):
    """check for arguments."""
    ac = Action(root)
    argument = ac.arguments[name]
    assert argument.name == name


action_minimal_input = parse_xml("""
    <action>
        <name>ForceTermination</name>
    </action>
""")

def test_Action_minimal_inp(root=action_minimal_input):
    """test for empty arguments dictionary"""
    ac = Action(root)
    assert len(ac.arguments) == 0
