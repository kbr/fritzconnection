# import shortcuts

__version__ = '1.0a1'

from .core import (
    FritzConnection,
    FritzConnectionException,
    FritzServiceError,
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
    ActionError,
)

package_version = __version__
