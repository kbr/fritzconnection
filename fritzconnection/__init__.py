# -*- coding: utf-8 -*-

# new since 0.6.5
package_version = '0.6.5'

from .fritzconnection import (
    FritzConnection,
    FritzInspection,
    print_servicenames,
    print_api,
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
