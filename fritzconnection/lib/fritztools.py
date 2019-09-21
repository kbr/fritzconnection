#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division


"""
helper functions.

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
                return '%3.1f %s' % (num, dimension)
            return '%3.1f %s%s' % (num, dimension, extension)
        num /= 1024
    return '%3.1f P%s' % (num, extension)


def format_rate(num, unit='bytes'):
    """
    Returns a human readable string of a byte/bits per second.
    If 'num' is bits, set unit='bits'.
    """
    return format_num(num, unit=unit) + '/s'
