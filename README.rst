
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


Python-Tool to communicate with the AVM FritzBox.
Uses the TR-064 protocol over UPnP.

Installation:
-------------

    pip install fritzconnection


Quickstart:
-----------

Pip will install a command line tool to inspect the FRITZ!Box-API. The APIs can differ depending on the FRITZ!Box model and the system software. ::

    $ fritzconnection -i <the_ip_address> -p <the_password> -s

This will list all available services. Both parameters ``the_ip_address`` and ``the_password`` are optional. If there is more than one Fritz!Box in the network, an address must be provided, because otherwise it's undefined which box will respond. Also most services are only accessible by providing a password. To list the ``actions`` of a ``service`` use the option ``-S`` with the 'servicename' as parameter, i.e.: ::

    $ fritzconnection -i <the_ip_address> -p <the_password> -S WLANConfiguration1

With the option ``-a`` and a 'servicename' given all parameters for the available ``actions`` are listet: ::

    $ fritzconnection -i <the_ip_address> -p <the_password> -a WLANConfiguration1

The option ``-A`` with 'servicename' and 'actionname' as parameter will also list ``direction`` and the ``data type`` of the action parameters: ::

    $ fritzconnection -i <the_ip_address> -p <the_password> -A WLANConfiguration1 GetGenericAssociatedDeviceInfo


An API-Call is made by the ``call_action``-method of the FritzConnection-Class. This method takes the ``servicename``, the ``actionname`` and optional arguments as parameter and may return a dictionary with the results (as described in the TR-064 protocoll description). A simple example is to reconnect for a new external ip: ::

    >>> from fritzconnection import FritzConnection
    >>> connection = FritzConnection()
    >>> connection.call_action('WANIPConn', 'ForceTermination')
    # or more comfortable:
    >>> connection.reconnect()

The latter wrapps the ``call_action``-method. For more complete examples look at the source-code of the modules in the ``fritzconnection/lib`` folder.


Documentation
-------------

The full documentation and release notes are at https://fritzconnection.readthedocs.org
