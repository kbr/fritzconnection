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
    Namespace object that also behaves like a dictionary, but is not
    iterable.

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

        >>> info = ArgumentNamespace(result, mapping)

    The `info` instance can now get used like a namespace object and
    like a dictionary: ::

        >>> info.serial_number
        '989BCB2B93B0'

        >>> info['modelname']
        'FRITZ!Box 7590'

    If no mapping is given, then `ArgumentNamespace` will consume the
    provided dictionary converting all keys from "MixedCase" style to
    "snake_case" removing the leading "new_" (removing "new_" can get
    turned of by setting `suppress_new` to `False`): ::

        >>> info = ArgumentNamespace(result)
        >>> info.up_time
        9516949

    If no mapping is given then also a sequence of the original
    Argument-names can provided as keyword-argument `extract` to get an
    ArgumentNamespace object with the subset of the "extracted
    arguments" and converted attribute names (to snake_case): ::

        >>> extract = "NewSerialNumber", "NewModelName"
        >>> info = ArgumentNamespace(result, extract=extract)
        >>> info.serial_number
        '989BCB2B93B0'
        >>> info.model_name
        'FRITZ!Box 7590'

    If `mapping` and `extract` are given, `mapping` has precedence and
    `extract` gets ignored.

    So by providing a mapping gives control about converting the
    attribute names and the number of attributes of the
    `ArgumentNamespace` instance. Providing no mapping will convert all
    attributes and providing no mapping but a series of original
    attribute names will extract the given subset of attributes.
    """

    def __init__(self, source, mapping=None, extract=None, suppress_new=True):
        if mapping is None:
            keys = extract if extract else source.keys()
            mapping = {
                self.rewrite_argument(key, suppress_new): key for key in keys
            }
        super().__init__(
            **{name: source[attribute] for name, attribute in mapping.items()}
        )

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __len__(self):
        # should provide len() as dict-like object
        return len(self.__dict__)

    @staticmethod
    def rewrite_argument(name, suppress_new=True):
        """
        Rewrite `name` from MixedCase to snake_case. So i.e. "MixedCase"
        gets converted to "mixed_case". The result may start with "new_"
        in case of AVM standard argument names. if `suppress_new` is
        `True` (the default) the prefix "new_" will get removed, so also
        "NewMixedCased" will get converted to "mixed_case".
        """
        new = "new_"
        result = "".join(
            f"_{char.lower()}" if char.isupper() else char for char in name
        )
        if result.startswith("_"):
            result = result[1:]
        if suppress_new and result.startswith(new):
            result = result[len(new):]
        return result
