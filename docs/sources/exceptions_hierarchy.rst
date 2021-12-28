**Exception Hierarchy:**

::

    FritzConnectionException
                    |
                    |--> ActionError --> FritzActionError
                    |--> ServiceError --> FritzServiceError
                    |
                    |--> FritzResourceError
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

