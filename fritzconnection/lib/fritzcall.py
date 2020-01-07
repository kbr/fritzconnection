"""
Module to access lists of recent phone calls: incoming, outgoing and
missed ones.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


import datetime

from ..core.processor import (
    processor,
    process_node,
    InstanceAttributeFactory,
    Storage,
)
from ..core.utils import get_xml_root
from .fritzbase import AbstractLibraryBase


__all__ = ['FritzCall', 'Call']


ALL_CALL_TYPES = 0
RECEIVED_CALL_TYPE = 1
MISSED_CALL_TYPE = 2
OUT_CALL_TYPE = 3

SERVICE = 'X_AVM-DE_OnTel1'


def datetime_converter(date_string):
    if not date_string:
        return date_string
    return datetime.datetime.strptime(date_string, '%d.%m.%y %H:%M')


def timedelta_converter(duration_string):
    if not duration_string:
        return duration_string
    hours, minutes = [int(part) for part in duration_string.split(':', 1)]
    return datetime.timedelta(hours=hours, minutes=minutes)


class FritzCall(AbstractLibraryBase):
    """
    Can dial phone numbers and gives access to lists of recent phone
    calls: incoming, outgoing and missed ones. All parameters are
    optional. If given, they have the following meaning: `fc` is an
    instance of FritzConnection, `address` the ip of the Fritz!Box,
    `port` the port to connect to, `user` the username, `password` the
    password, `timeout` a timeout as floating point number in seconds,
    `use_tls` a boolean indicating to use TLS (default False).
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.calls = None

    def _update_calls(self, num=None, days=None):
        result = self.fc.call_action(SERVICE, 'GetCallList')
        url = result['NewCallListURL']
        if days:
            url += f'&days={days}'
        elif num:
            url += f'&max={num}'
        root = get_xml_root(url, session=self.fc.session)
        self.calls = CallCollection(root)

    def get_calls(self, calltype=ALL_CALL_TYPES, update=True,
                        num=None, days=None):
        """
        Return a list of Call instances of type calltypes. If calltype
        is 0 all calls are listet. If *update* is True, all calls are
        reread from the router. *num* maximum number of entries in call
        list. *days* number of days to look back for calls e.g. 1: calls
        from today and yesterday, 7: calls from the complete last week.
        """
        if not self.calls:
            update = True
        if update:
            self._update_calls(num, days)
        if calltype == ALL_CALL_TYPES:
            return self.calls.calls
        return [call for call in self.calls if call.type == calltype]

    def get_received_calls(self, update=True, num=None, days=None):
        """
        Return a list of Call instances of received calls. If *update*
        is True, all calls are reread from the router. *num* maximum
        number of entries in call list. *days* number of days to look
        back for calls e.g. 1: calls from today and yesterday, 7: calls
        from the complete last week.
        """
        return self.get_calls(RECEIVED_CALL_TYPE, update, num, days)

    def get_missed_calls(self, update=True, num=None, days=None):
        """
        Return a list of Call instances of missed calls. If *update* is
        True, all calls are reread from the router. *num* maximum number
        of entries in call list. *days* number of days to look back for
        calls e.g. 1: calls from today and yesterday, 7: calls from the
        complete last week.
        """
        return self.get_calls(MISSED_CALL_TYPE, update, num, days)

    def get_out_calls(self, update=True, num=None, days=None):
        """
        Return a list of Call instances of outgoing calls. If *update*
        is True, all calls are reread from the router. *num* maximum
        number of entries in call list. *days* number of days to look
        back for calls e.g. 1: calls from today and yesterday, 7: calls
        from the complete last week.
        """
        return self.get_calls(OUT_CALL_TYPE, update, num, days)

    def dial(self, number):
        """
        Dials the given *number* (number must be a string, as phone
        numbers are allowed to start with leading zeros). This method
        has no return value, but will raise an error reported from the
        Fritz!Box on failure. **Note:** The dial-help of the Fritz!Box
        must be activated to make this work.
        """
        arg = {'NewX_AVM-DE_PhoneNumber': number}
        self.fc.call_action('X_VoIP1', 'X_AVM-DE_DialNumber', arguments=arg)


class AttributeConverter:
    """
    Data descriptor returning converted attribute values.
    """
    def __init__(self, attribute_name, converter=str):
        self.attribute_name = attribute_name
        self.converter = converter

    def __set__(self, obj, value):
        return NotImplemented

    def __get__(self, obj, objtype):
        attr = getattr(obj, self.attribute_name)
        try:
            attr = self.converter(attr)
        except (TypeError, ValueError):
            pass
        return attr


@processor
class Call:
    """
    Represents a call with the attributes provided by AVM. Instance
    attributes are *Id*, *Type*, *Called*, *Caller*, *CallerNumber*,
    *CalledNumber*, *Name*, *Device*, *Port*, *Date*, *Duration* and
    *Count*. The spelling represents the original xml-node names.
    Additionally the following attributes can be accessed by lowercase
    names: *id* returning the Id as integer, *type* returning the Type
    as integer, *date* returning the Date as datetime-instance,
    *duration* returning the Duration as timedelta-instance.
    """
    id = AttributeConverter('Id', int)
    type = AttributeConverter('Type', int)
    date = AttributeConverter('Date', datetime_converter)
    duration = AttributeConverter('Duration', timedelta_converter)

    def __init__(self):
        self.Id = None
        self.Type = None
        self.Called = None
        self.Caller = None
        self.CallerNumber = None
        self.CalledNumber = None
        self.Name = None
        self.Device = None
        self.Port = None
        self.Date = None
        self.Duration = None
        self.Count = None

    def __str__(self):
        number = self.Called if self.type == 3 else self.Caller
        duration = self.Duration if self.type != 2 else "-"
        if not number:
            number = "-"
        return f'{self.Type:>6}   {number:24}{self.Date:>18}{duration:>12}'


class CallCollection(Storage):
    """
    Container for a sequence of Call instances.
    """
    Call = InstanceAttributeFactory(Call)

    def __init__(self, root):
        self.timestamp = None
        self.calls = list()
        super().__init__(self.calls)
        process_node(self, root)

    def __iter__(self):
        return iter(self.calls)
