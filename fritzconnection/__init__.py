# -*- coding: utf-8 -*-


from .fritzconnection import (
    FritzConnection,
    FritzInspection,
    print_servicenames,
    print_api,
    get_version,
    ServiceError,
    ActionError,
    AuthorizationError,
)
from . fritzcall import FritzCall
from . fritzcallforwarding import (
    FritzCallforwarding,
    print_callforwardings,
)
from .fritzhosts import (
    FritzHosts,
    print_hosts,
)
from .fritzphonebook import (
    FritzPhonebook,
    print_phonebooks,
)
from .fritzstatus import (
    FritzStatus,
    print_status,
)
from .fritzwlan import FritzWLAN


# same as fritzconnection core module:
package_version = get_version()
