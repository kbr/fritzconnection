"""
Abstract base class for all library classes.
"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


from ..core.fritzconnection import (
    FritzConnection,
    DEFAULT_POOL_CONNECTIONS,
    DEFAULT_POOL_MAXSIZE,
)


class AbstractLibraryBase:
    """
    Abstract base class for library classes. Implements the common
    initialisation. All parameters are optional. If given, they have the
    following meaning: `fc` is an instance of FritzConnection, `address`
    the ip of the Fritz!Box, `port` the port to connect to, `user` the
    username, `password` the password, `timeout` a timeout as floating
    point number in seconds, `use_tls` a boolean indicating to use TLS
    (default False). `pool_connections` and `pool_maxsize` are to
    override the urllib3 default settings.
    """
    def __init__(self, fc=None, address=None, port=None, user=None,
                 password=None, timeout=None, use_tls=False,
                 pool_connections=DEFAULT_POOL_CONNECTIONS,
                 pool_maxsize=DEFAULT_POOL_MAXSIZE,
        ):
        if fc is None:
            kwargs = {
                k:v for k, v in locals().items() if k not in ('self', 'fc')
            }
            fc = FritzConnection(**kwargs)
        self.fc = fc

    @property
    def modelname(self):
        """
        The device modelname. Every library module derived from
        `AbstractLibraryBase` inherits this property.
        """
        return self.fc.modelname
