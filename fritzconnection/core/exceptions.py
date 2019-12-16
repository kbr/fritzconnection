"""
Module defining fritzconnection specific exceptions.
"""

# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer
#
#
# Exception Inheritance:
# ----------------------
#
# FritzConnectionException
#                 |
#                 |--> ActionError --> FritzActionError
#                 |--> ServiceError --> FritzServiceError
#                 |
#                 |--> FritzArgumentError
#                 |       |
#                 |       |--> FritzArgumentValueError
#                 |               |
#                 |               |--> FritzArgumentStringToShortError
#                 |               |--> FritzArgumentStringToLongError
#                 |               |--> FritzArgumentCharacterError
#                 |
#                 |--> FritzInternalError
#                 |       |
#                 |       |--> FritzActionFailedError
#                 |       |--> FritzOutOfMemoryError
#                 |
#                 |--> FritzSecurityError
#                 |
#                 |-->|--> FritzLookUpError
#                 |   |
# KeyError -------+-->|
#                 |
#                 |
#                 |-->|--> FritzArrayIndexError
#                     |
# IndexError -------->|
#
#


# export all Exceptions on * imports
__all__ = [
    'FritzConnectionException',
    'FritzActionError',
    'FritzActionFailedError',
    'FritzArgumentCharacterError',
    'FritzArgumentError',
    'FritzArgumentStringToLongError',
    'FritzArgumentStringToShortError',
    'FritzArgumentValueError',
    'FritzArrayIndexError',
    'FritzInternalError',
    'FritzLookUpError',
    'FritzOutOfMemoryError',
    'FritzSecurityError',
    'FritzServiceError',
]


class FritzConnectionException(Exception):
    """Base Exception for communication errors with the Fritz!Box"""


class ActionError(FritzConnectionException):
    """
    Exception raised by calling nonexisting actions.
    Legathy Exception. Use FritzActionError instead.
    """


class ServiceError(FritzConnectionException):
    """
    Exception raised by calling nonexisting services.
    Legathy Exception. Use FritzServiceError instead.
    """


class FritzServiceError(ServiceError):
    """Exception raised by calling nonexisting services."""


class FritzActionError(ActionError):
    """Exception raised by calling nonexisting actions."""


class FritzArgumentError(FritzConnectionException):
    """Exception raised by invalid arguments."""


class FritzArgumentValueError(FritzArgumentError):
    """
    Exception raised by arguments with invalid values.
    Inherits from the more generic FritzArgumentError.
    """


class FritzArgumentStringToShortError(FritzArgumentValueError):
    """
    Exception raised by arguments with invalid string length for the
    string being to short. Inherits from the more generic
    FritzArgumentValueError.
    """


class FritzArgumentStringToLongError(FritzArgumentValueError):
    """
    Exception raised by arguments with invalid string length for the
    string being to long. Inherits from the more generic
    FritzArgumentValueError.
    """


class FritzArgumentCharacterError(FritzArgumentValueError):
    """
    Exception raised by arguments with invalid characters.
    Inherits from the more generic FritzArgumentValueError.
    """


class FritzInternalError(FritzConnectionException):
    """Exception raised by panic in the box."""


class FritzActionFailedError(FritzInternalError):
    """
    Exception raised by the box unable to execute the action properly.
    Inherits from the more generic FritzInternalError.
    """


class FritzOutOfMemoryError(FritzInternalError):
    """
    Exception raised by memory shortage of the box.
    Inherits from the more generic FritzInternalError.
    """


class FritzSecurityError(FritzConnectionException):
    """Authorization error or wrong security context."""


class FritzLookUpError(FritzConnectionException, KeyError):
    """
    Lookup for id or entry in existing internal array failed.
    Inherits from KeyError.
    So KeyError can also be used for exception handling.
    """


class FritzArrayIndexError(FritzConnectionException, IndexError):
    """
    Addressing an entry in an internal array by index failed.
    Inherits from IndexError.
    So IndexError can also be used for exception handling.
    """


# Collection of error codes and corresponding exceptions:
FRITZ_ERRORS = {
    '401': FritzActionError,
    '402': FritzArgumentError,
    '501': FritzActionFailedError,
    '600': FritzArgumentValueError,
    '603': FritzOutOfMemoryError,
    '606': FritzSecurityError,
    '713': FritzArrayIndexError,
    '714': FritzLookUpError,
    '801': FritzArgumentStringToShortError,
    '802': FritzArgumentStringToLongError,
    '803': FritzArgumentCharacterError,
    '820': FritzInternalError,
}
