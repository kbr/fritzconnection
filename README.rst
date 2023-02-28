
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
Supports the TR-064 and the (AHA-)HTTP-Interface.


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

Here the *fc.reconnect()* is a shortcut.

FritzConnection provides two basic commands to communicate with the router: *call_action()* for the TR-064 API and *call_http()* for the HTTP-API. Both APIs can be used on a FritzConnection instance side by side.

TR-064
......

The basic method FritzConnection provides to access the FritzOS-API is the *call_action()* method. A reconnection by means of *call_action()* would look like this: ::

    fc = FritzConnection(address='192.168.178.1')
    fc.call_action("WANIPConn1", "ForceTermination")

The method *call_action()* expects a service- and an action-name (and optional arguments). In general FritzConnection can execute every service and action provided by the (model-specific) API as documented by AVM. For i.e. this can be network settings, status informations, access to home automation devices and much more. In case a call to the FritzOS-API provides information the *call_action()* method returns a dictionary with the results.

HTTP
....

This interface provides access to homeautomation-devices using the *call_http()* method. The command "getbasicdevicestats" is an example to retrieve information not available by the TR-064 API: ::

    fc = FritzConnection(
        address='192.168.178.1', user="username", password="password"
    )
    fc.call_http("getbasicdevicestats", "12345 7891011")

As arguments this method takes a command and an identifier for the device and returns a dictionary with the content-type, the encoding and the response data.


Username and password
.....................

Some TR-064 calls are available without a username and password, for using the http-interface both are required. To avoid hardcoding FritzConnection can read user and password from the environment variables FRITZ_USERNAME and FRITZ_PASSWORD.


Caching
.......

Instanciating FritzConnection can take some time. To speed up things use a cache: ::

    fc = FritzConnection(..., use_cache=True)

By default this argument is 'False'. After creating the cache FritzConnection will start up much more faster the next time.


Library
-------

The package comes with some library-modules as examples how to implement applications on top of FritzConnection.


Documentation
-------------

The full documentation and release notes are at https://fritzconnection.readthedocs.org
