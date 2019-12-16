**Exception Hierarchy:**

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

