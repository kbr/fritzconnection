
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
Uses the TR-064 protocol.

Installation:
-------------

    pip install fritzconnection


Available Modules, Commands and Tools
-------------------------------------

``fritzconnection.py`` makes the SOAP interface of the FRITZ!Box available on the command line.
Shows all available services and actions when run with the argument ``-c``. Use ``-h`` for help.

This is the main module and works standalone. The other modules listet here are utility modules for convenience and examples on how to use fritzconnection.

``fritzstatus.py`` is a command line interface to display status information of the FRITZ!Box.
It also serves as an example on how to use the fritzconnection module.

``fritzmonitor.py`` is a Tkinter GUI to display current IP as well as the upstream and downstream rates.
It also makes it easy to reconnect and thus get a different IP from your ISP.

``fritzhosts.py`` is a command line interface to display the hosts known by the FRITZ!Box with IP, name, MAC and status.

``fritzwlan.py`` Utility module for FritzConnection to list the known WLAN connections.

``fritzcallforwarding.py`` Utility module for FritzConnection to manage callforwardings.

``fritzphonebook.py`` Utility module for FritzConnection to access phone books.

``fritzcall.py`` Gives access to recent phone calls: incoming, outgoing and missed ones.


Other Files
-----------

``fritztools.py`` contains some helper functions and ``test.py`` contains unit tests.

Quickstart:
-----------

Inspect the API:

    >>> import fritzconnection as fc
    >>> fc.print_api(password='your_password')

An API-Call is made by the ``call_action``-method of the FritzConnection-Class. This method takes the ``servicename``, the ``actionname`` and optional arguments as parameter and may return a dictionary with the results (as described in the TR-064 protocoll description). A simple example is to reconnect for a new external ip:

    >>> from fritzconnection import FritzConnection
    >>> connection = FritzConnection()
    >>> connection.call_action('WANIPConnection', 'ForceTermination')
    # or more comfortable:
    >>> connection.reconnect()

The latter wrapps the ``call_action``-method. For a more complete example look at the ``fritzhosts.py`` souce-code.


Documentation
-------------

The full documentation and release notes are at https://fritzconnection.readthedocs.org
