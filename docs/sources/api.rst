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

As a shortcut FritzConnection can get imported by: ::

    from fritzconnection import FritzConnection


fritzconnection
...............

.. automodule:: fritzconnection.core.fritzconnection
    :members:


fritzmonitor
............

The FritzMonitor class provides an event-queue with call-events. Events are of type string. ::

    from fritzconnection.core.fritzmonitor import FritzMonitor

    fm = FritzMonitor()
    event_queue = fm.start()
    # handle events from the queue for further processing here ...
    fm.stop()

For a more detailed example refer to 'fritzconnection.cli.fritzmonitor.py'.

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

