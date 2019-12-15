Internal api
============


Internally fritzconnection is structured into subpackages: ::


    fritzconnection --|-- cli
                      |-- core --|-- devices
                      |          |-- exceptions
                      |          |-- fritzconnection
                      |          |-- processor
                      |          |-- soaper
                      |          |-- utils
                      |
                      |-- lib ---|-- fritzhosts
                      |          |-- fritzstatus
                      |
                      |-- tests


The package ``cli`` implements the entry-points for command line usage, the tests are in the ``tests`` package and the library modules are in ``lib``. The implementation of fritzconnection itself is structured in the ``core`` package. This section is about the internal api of the core package.


fritzconnection
---------------

.. automodule:: fritzconnection.core.fritzconnection
    :members:


exceptions
----------

::

    FritzConnectionException
                    |
                    |--> ActionError --> FritzActionError
                    |--> ServiceError --> FritzServiceError
                    |
                    |--> FritzArgumentError
                    |       |
                    |       |--> FritzArgumentValueError
                    |               |
                    |               |--> FritzArgumentStringToShortError
                    |               |--> FritzArgumentStringToLongError
                    |               |--> FritzArgumentCharacterError
                    |
                    |--> FritzInternalError
                    |       |
                    |       |--> FritzActionFailedError
                    |       |--> FritzOutOfMemoryError
                    |
                    |--> FritzSecurityError
                    |
                    |-->|--> FritzLookUpError
                    |   |
    KeyError -------+-->|
                    |
                    |
                    |-->|--> FritzArrayIndexError
                        |
    IndexError -------->|


.. automodule:: fritzconnection.core.exceptions
    :members:


devices
-------

.. automodule:: fritzconnection.core.devices
    :members:


soaper
------

.. automodule:: fritzconnection.core.soaper
    :members:


processor
---------

.. automodule:: fritzconnection.core.processor
    :members:
