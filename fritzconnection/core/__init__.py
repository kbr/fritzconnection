# import shortcuts

from .fritzconnection import (
    FritzConnection,
    FRITZ_IP_ADDRESS,
    FRITZ_TCP_PORT,
    FRITZ_USERNAME,
)

from .exceptions import (
    FritzConnectionException,
    FritzActionError,
    FritzArgumentError,
    FritzActionFailedError,
    FritzArgumentValueError,
    FritzOutOfMemoryError,
    FritzSecurityError,
    FritzArrayIndexError,
    FritzLookUpError,
    FritzArgumentStringToShortError,
    FritzArgumentStringToLongError,
    FritzArgumentCharacterError,
    FritzInternalError,
    ServiceError,
    ActionError
)
