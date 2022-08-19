"""
Some helper functions for the library.
"""

import math
from types import SimpleNamespace


def byte_formatter(value):
    """
    Gets a large integer als value and returns a tuple with the value as
    float and the matching dimension as string, i.e.
    >>> byte_formatter(242981246)
    (242.981246, 'MB')
    Expects positive integer as input. Negative numbers are interpreted
    as positive numbers. values < 1 are interpreted as 0.
    """
    dim = ['B', 'KB', 'MB', 'GB', 'TB']
    value = abs(value)
    if value < 1:
        log = 0
        num = 0
    else:
        log = min(int(math.log10(value) / 3), len(dim))
        num = value / 1000 ** log
    try:
        dimension = dim[log]
    except IndexError:
        dimension = 'PB'
    return num, dimension


def format_num(num, unit='bytes'):
    """
    Returns a human-readable string of a byte-value.
    If 'num' is bits, set unit='bits'.
    """
    num, dim = byte_formatter(num)
    if unit != 'bytes':
        dim += 'it'  # then its Bit by default
    return f'{num:3.1f} {dim}'


def format_rate(num, unit='bytes'):
    """
    Returns a human-readable string of a byte/bits per second.
    If 'num' is bits, set unit='bits'.
    """
    return format_num(num, unit=unit) + '/s'


def format_dB(num):
    """
    Returns a human-readable string of dB. The value is divided
    by 10 to get first decimal digit
    """
    num /= 10
    return f'{num:3.1f} {"dB"}'


class ArgumentNamespace(SimpleNamespace):
    """
    Namespace object that also behaves like a dictionary.

    Usecase is as a wrapper for the dictionary returned from
    `FritzConnection.call_action()`. This dictionary has keys named
    "arguments" as described by the AVM documentation, combined with
    values as the corresponding return values. Instances of
    `ArgumentNamespace` can get used to extract a subset of this
    dictionary and transfer the Argument-names to more readable
    ones. For example consider that `fc` is a FritzConnection instance.
    Then the following call: ::

        result = fc.call_action("DeviceInfo1", "GetInfo")

    will return a dictionary like: ::

        {'NewManufacturerName': 'AVM',
         'NewManufacturerOUI': '00040E',
         'NewModelName': 'FRITZ!Box 7590',
         'NewDescription': 'FRITZ!Box 7590 154.07.29',
         'NewProductClass': 'AVMFB7590',
         'NewSerialNumber': '989BCB2B93B0',
         'NewSoftwareVersion': '154.07.29',
         'NewHardwareVersion': 'FRITZ!Box 7590',
         'NewSpecVersion': '1.0',
         'NewProvisioningCode': '000.044.004.000',
         'NewUpTime': 9516949,
         'NewDeviceLog': 'long string here ...'}

    In case that just the model name and serial number are of interest,
    and should have better names, first define a mapping: ::

        mapping = {
            "modelname": "NewModelName",
            "serial_number": "NewSerialNumber"
        }

    and use this `mapping` with the `result` to create an `ArgumentNamespace`
    instance: ::

        info = ArgumentNamespace(mapping, result)

    The `info` instance can now get used like a namespace object and
    like a dictionary: ::

        >>> info.serial_number
        >>> '989BCB2B93B0'

        >>> info['modelname']
        >>> 'FRITZ!Box 7590'

    """
    def __init__(self, mapping, source):
        super().__init__(
            **{name: source[attribute] for name, attribute in mapping.items()}
        )

    def __getitem__(self, key):
        return getattr(self, key)

