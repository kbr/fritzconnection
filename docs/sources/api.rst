Structure and API
=================


fritzconnection is structured into subpackages: ::


    fritzconnection --|-- cli
                      |-- core --|-- devices
                      |          |-- exceptions
                      |          |-- fritzconnection
                      |          |-- fritzmonitor
                      |          |-- processor
                      |          |-- soaper
                      |          |-- utils
                      |
                      |-- lib
                      |-- tests


The package ``cli`` implements the entry-points for command line usage, the tests are in the ``tests`` package and the library modules are in ``lib``. The implementation of fritzconnection itself is structured in the ``core`` package.


Public API
----------

The public interface is provided by the FritzConnection class, the fritzmonitor- and the exceptions-module.

There are shortcuts to import FritzConnection and FritzMonitor: ::

    from fritzconnection import FritzConnection
    from fritzconnection import FritzMonitor


fritzconnection
...............

.. automodule:: fritzconnection.core.fritzconnection
    :members:


fritzmonitor
............

.. automodule:: fritzconnection.core.fritzmonitor
    :members:



exceptions
..........

Exceptions can get imported by: ::

    from fritzconnection.core.exceptions import FritzServiceError
    # or:
    from fritzconnection.core.exceptions import *

The latter style is often discouraged because of possible namespace-pollution, less clarity about the origin of imported objects and potential name clashings. By using a * import fritzconnection will just import exceptions starting with ``Fritz`` in their names.

.. include:: exceptions_hierarchy.rst

.. automodule:: fritzconnection.core.exceptions
    :members:

**Legathy Exceptions:**

.. autoexception:: fritzconnection.core.exceptions.ActionError
.. autoexception:: fritzconnection.core.exceptions.ServiceError



Internal API
------------

The devices-, processor- and soaper-module don't provide a public interface and are used internally.

devices
.......

.. automodule:: fritzconnection.core.devices
    :members:


processor
.........

.. automodule:: fritzconnection.core.processor
    :members:


soaper
......

.. automodule:: fritzconnection.core.soaper
    :members:

