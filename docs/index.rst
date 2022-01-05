.. fritzconnection documentation master file, created by
   sphinx-quickstart on Tue Mar 19 10:09:48 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


fritzconnection documentation
=============================


fritzconnection is a `Python <https://www.python.org/>`_ library to communicate with the `AVM Fritz!Box <https://en.avm.de/produkte/fritzbox/>`_ by the TR-064 protocol. This allows to read status-information from the router, read and change configuration settings and state, monitor realtime phone calls and much more.

.. image:: fritzconnection-360x76.png

The available services are depending on the Fritz!Box model and the according system software. fritzconnection can list and access all available services and actions of a given router. Using fritzconnection is as easy as: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.178.1')
    fc.reconnect()  # get a new external ip from the provider
    print(fc)  # print router model information

fritzconnection provides a basic API `call_action()` that takes a service- and an action-name with optional arguments to send commands and receive data. In the example above the `reconnect()` method just wraps the `call_action()` method. A reconnection by means of `call_action()` would look like this: ::

    fc = FritzConnection(address='192.168.178.1')
    fc.call_action("WANIPConn1", "ForceTermination")

With the `call_action()` method every service/action combination documented by the `AVM support-page (Apps/TR-064) <https://avm.de/service/schnittstellen/>`_ can get executed.

fritzconnection comes with a library to make some common tasks easier. For a detailed overview refer to the :doc:`sources/introduction` and the documentation of the :doc:`library <sources/library>`.



.. note::
   fritzconnection is neither related nor supported by AVM. Also AVM reserves the right to add, modify or remove features of their products at any time without notice.


.. toctree::
   :maxdepth: 1
   :caption: Contents:


   sources/install
   sources/introduction
   sources/call_monitoring
   sources/library
   sources/api
   sources/further_reading
   sources/changes
   sources/authors
   sources/license



