.. fritzconnection documentation master file, created by
   sphinx-quickstart on Tue Mar 19 10:09:48 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.


fritzconnection documentation
=============================


fritzconnection is a `Python <https://www.python.org/>`_ library to communicate with the `AVM Fritz!Box <https://en.avm.de/produkte/fritzbox/>`_ by the TR-064 protocol, the AHA-HTTP-Interface and also provides call-monitoring. This allows to read status-information from the router, read and change configuration settings and state, interact with smart-home-devices and monitor realtime phone calls.

.. image:: fritzconnection-360x76.png

The available features are depending on the Fritz!Box model and the according system software. Using fritzconnection is as easy as: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address="192.168.178.1", user="user", password="pw")
    print(fc)  # print router model information

    # tr-064 interface: reconnect for a new ip
    fc.call_action("WANIPConn1", "ForceTermination")
    fc.reconnect()  # do the same with a shortcut

    # http interface: get history data from a device with given 'ain'
    fc.call_http("getbasicdevicestats", "12345 7891011")

FritzConnection provides two basic commands to communicate with the router APIs: *call_action()* for the TR-064-Interface and *call_http()* for the (AHA)-HTTP-Interface. Both APIs can be used on the same FritzConnection instance side by side.

``call_action()`` expects a **TR-064** service- and an action-name (and optional arguments). In general FritzConnection can execute every service and action provided by the (model-specific) API as documented by AVM. For i.e. this can be network settings, status informations, access to home automation devices and much more. The *call_action()* method returns the response from the router as a dictionary with the values already converted to the matching Python datatypes.

``call_http()`` expects a command for the **http-interface** like "getbasicdevicestats" and, depending on the command, additional arguments like a device "ain" (identifier). A call to the method returns a dictionary with the *content-type*, the *encoding* and the *response* data of the http-response. The content-type of the response-data is typical "text/plain" or "text/xml" and may need further processing.

With the `call_action()` and `call_http()` methods every service/action-combination and command documented by the `AVM support-page (Apps/TR-064, HTTP) <https://avm.de/service/schnittstellen/>`_ can get executed.

The fritzconnection-package comes with a library to make some common tasks easier and can also serve as example code. For a detailed overview refer to :doc:`sources/getting_started` and the documentation of the :doc:`library <sources/library_modules>`.


.. note::
   fritzconnection is neither related nor supported by AVM. Also AVM reserves the right to add, modify or remove features of their products at any time without notice. Furthermore the terms "AVM", "Fritz!Box" and "Fritz!OS" are trademarks of `AVM Computersysteme Vertriebs GmbH <https://avm.de/impressum/>`_.


.. toctree::
   :maxdepth: 1
   :caption: Contents:


   sources/installation
   sources/getting_started
   sources/fritzconnection_api
   sources/library_modules
   sources/call_monitoring
   sources/further_reading
   sources/version_history
   sources/authors
   sources/license



