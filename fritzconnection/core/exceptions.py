"""
fritzconnection specific exceptions.

This module is part of the FritzConnection package.
https://github.com/kbr/fritzconnection
License: MIT - tldr: USAGE IS FREE AND ENTIRELY AT OWN RISK!
Author: Klaus Bremer
"""


class FritzConnectionException(Exception):
    """Base Exception for communication errors with the Fritz!Box"""


class FritzServiceError(FritzConnectionException):
    """Exception raised by calling nonexisting services."""


class FritzActionError(FritzConnectionException):
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
    Exception raised by arguments with invalid string length.
    Inherits from the more generic FritzArgumentValueError.
    """


class FritzArgumentStringToLongError(FritzArgumentValueError):
    """
    Exception raised by arguments with invalid string length.
    Inherits from the more generic FritzArgumentValueError.
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
    Exception raised by box unable to run the action.
    Inherits from the more generic FritzInternalError.
    """


class FritzOutOfMemoryError(FritzInternalError):
    """
    Exception raised by memory shortage of the box.
    Inherits from the more generic FritzInternalError.
    """


class FritzSecurityError(FritzConnectionException):
    """Authorization error or wrong security context."""


class FritzLookupError(FritzConnectionException, KeyError):
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


class ActionError(FritzActionError):
    """
    Exception raised by calling nonexisting actions.
    Legathy Exception. Use FritzActionError instead.
    """


class ServiceError(FritzServiceError):
    """
    Exception raised by calling nonexisting services.
    Legathy Exception. Use FritzServiceError instead.
    """


FRITZ_ERRORS = {
    '401': FritzActionError,
    '402': FritzArgumentError,
    '501': FritzActionFailedError,
    '600': FritzArgumentValueError,
    '603': FritzOutOfMemoryError,
    '606': FritzSecurityError,
    '713': FritzArrayIndexError,
    '714': FritzLookupError,
    '801': FritzArgumentStringToShortError,
    '802': FritzArgumentStringToLongError,
    '803': FritzArgumentCharacterError,
    '820': FritzInternalError,
}

