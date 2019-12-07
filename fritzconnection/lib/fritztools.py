"""
Some helper functions for more readable bits and bytes.
"""


def format_num(num, unit='bytes'):
    """
    Returns a human readable string of a byte-value.
    If 'num' is bits, set unit='bits'.
    """
    if unit == 'bytes':
        extension = 'B'
    else:
        # if it's not bytes, it's bits
        extension = 'Bit'
    for dimension in (unit, 'K', 'M', 'G', 'T'):
        if num < 1024:
            if dimension == unit:
                return f'{num:3.1f} {dimension}'
            return f'{num:3.1f} {dimension}{extension}'
        num /= 1024
    return f'{num:3.1f} P{extension}'


def format_rate(num, unit='bytes'):
    """
    Returns a human readable string of a byte/bits per second.
    If 'num' is bits, set unit='bits'.
    """
    return format_num(num, unit=unit) + '/s'
