# import shortcuts

__version__ = '1.0_alpha_1'

from .core import (
    FritzConnection,
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
    ActionError,
)

package_version = __version__
