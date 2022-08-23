
===============
fritzconnection
===============


.. image::
    https://img.shields.io/pypi/pyversions/fritzconnection.svg
    :alt: Python versions
    :target: https://pypi.org/project/fritzconnection/

.. image::
    https://img.shields.io/pypi/l/fritzconnection.svg
    :target: https://pypi.org/project/fritzconnection/


Python-Tool to communicate with the AVM Fritz!Box.
Uses the TR-064 protocol over UPnP.

Installation:
-------------

For installation use pip ::

    $ pip install fritzconnection
      or
    $ pip install fritzconnection[qr]

The latter will install the dependency to enable QR-code creation for wifi login.

Quickstart:
-----------

Using fritzconnection is as easy as: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.178.1')
    fc.reconnect()  # get a new external ip from the provider
    print(fc)  # print router model informations

Here the *fc.reconnect()* is a shortcut. The basic method FritzConnection provides to access the FritzOS-API is the *call_action()* method. A reconnection by means of *call_action()* would look like this: ::

    fc = FritzConnection(address='192.168.178.1')
    fc.call_action("WANIPConn1", "ForceTermination")

The method *call_action()* expects a service- and an action-name (and optional arguments). In general FritzConnection can execute every service and action provided by the (model-specific) API as documented by AVM. For i.e. this can be network settings, status informations, access to home automation devices and much more. In case a call to the FritzOS-API provides information the *call_action()* method returns a dictionary with the results.

The package comes with some library-modules as examples how to implement applications on top of FritzConnection.


Documentation
-------------

The full documentation and release notes are at https://fritzconnection.readthedocs.org
