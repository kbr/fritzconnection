"""
Abstract base class for all library classes.

An internal module providing the `AbstractLibraryBase` class. This is an
abstract class that should not get instantiated but should serve as a
base class for library classes providing a common initialisation.

"""
# This module is part of the FritzConnection package.
# https://github.com/kbr/fritzconnection
# License: MIT (https://opensource.org/licenses/MIT)
# Author: Klaus Bremer


from __future__ import annotations

from ..core.fritzconnection import FritzConnection


class AbstractLibraryBase:
    """
    Abstract base class for library classes. Implements the common
    initialisation. The first argument `fc` can be a FritzConnection
    instance. If this argument is given no further arguments are needed.
    If the argument `fc` is not given, all other arguments are forwarded
    to get a FritzConnection instance. These arguments have the same
    meaning as for `FritzConnection.__init__()`. Using positional
    arguments is strongly discouraged. Use keyword arguments instead.
    """
    def __init__(
        self,
        fc: FritzConnection | None = None,
        *args,
        **kwargs
    ):
        if fc is None:
            fc = FritzConnection(*args, **kwargs)
        self.fc = fc

    @property
    def modelname(self) -> str:
        """
        The device modelname. Every library module derived from
        `AbstractLibraryBase` inherits this property.
        """
        return self.fc.modelname
