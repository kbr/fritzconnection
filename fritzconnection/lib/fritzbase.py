from ..core.fritzconnection import FritzConnection


class AbstractLibraryBase:
    """
    Abstract base class for library classes. Implements the common
    initialisation. All parameters are optional. If given, they have the
    following meaning: `fc` is an instance of FritzConnection, `address`
    the ip of the Fritz!Box, `port` the port to connect to, `user` the
    username, `password` the password, `timeout` a timeout as floating
    point number in seconds, `use_tls` a boolean indicating to use TLS
    (default False).
    """

    def __init__(
        self,
        fc: FritzConnection | None = None,
        address: str | None = None,
        port:int | None = None,
        user:str | None = None,
        password:str | None = None,
        timeout:int | None = None,
        use_tls:bool | None = None,
    ) -> None:
        if fc is None:
            kwargs = {k: v for k, v in locals().items() if k not in ("self", "fc")}
            fc = FritzConnection(**kwargs)
        self.fc = fc

    @property
    def modelname(self) -> str:
        """
        The device modelname. Every library module derived from
        `AbstractLibraryBase` inherits this property.
        """
        return self.fc.modelname
