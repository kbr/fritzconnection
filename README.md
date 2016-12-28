## fritzconnection

Python-Tool to communicate with the AVM FritzBox.
Uses the TR-064 protocol.

### Installation:

    pip install fritzconnection

### Dependencies

fritzconnection requires the python modules `lxml` and `requests`:

    pip install lxml requests

### Available Modules, Commands and Tools

`fritzconnection.py` makes the SOAP interface of the FRITZ!Box available on the command line.
Shows all available services and actions when run with the argument `-c`.

`fritzstatus.py` is a command line interface to display status information of the FRITZ!Box.
It also serves as an example on how to use the fritzconnection module.

`fritzmonitor.py` is a Tkinter GUI to display current IP as well as the upstream and downstream rates.
It also makes it easy to reconnect and thus get a different IP from your ISP.

`fritzhosts.py` is a command line interface to display the hosts known by the FRITZ!Box with IP, name, MAC and status.

### Other Files

`fritztools.py` contains some helper functions and `test.py` contains unit tests.

### Quickstart:

Inspect the API:

    >>> import fritzconnection as fc
    >>> fc.print_api(password='your_password')

An API-Call is made by the `call_action`-method of the FritzConnection-Class. This method takes the `servicename`, the `actionname` and optional arguments as parameter and may return a dictionary with the results (as described in the TR-064 protocoll description). A simple example is to reconnect for a new external ip:

    >>> from fritzconnection import FritzConnection
    >>> connection = FritzConnection()
    >>> connection.call_action('WANIPConnection', 'ForceTermination')
    # or more comfortable:
    >>> connection.reconnect()

The latter wrapps the `call_action`-method. For a more complete example look at the `fritzhosts.py` souce-code.


#### Changed with version 0.6:

FritzConnection now uses long qualified names as `servicename`, i.e. `WLANConfiguration:1` or `WLANConfiguration:2`. So these servicenames can now be used to call actions on different services with the same name:

    >>> connection = FritzConnection()
    >>> info = connection.call_action('WANIPConnection:2', 'GetInfo')

For backward compatibility servicename-extensions like ':2' can be omitted on calling 'call_action'. In this case FritzConnection will use the extension ':1' as default.

On calling unknown services or actions in both cases KeyErrors has been raised. Calling an unknown service (or one unaccessible without a password) will now raise a `ServiceError`. Calling an invalid action on a service will raise an `ActionError`. Both Exceptions are Subclasses from the new `FritzConnectionException`. The Exception classes can get imported from fritzconnection:

    >>> from fritzconnection import ServiceError, ActionError


### Resources

* [The Source Code of fritzconnection](https://bitbucket.org/kbr/fritzconnection)
* Information on TR-064:
  * [AVM's manual First Steps with TR-064](http://avm.de/fileadmin/user_upload/Global/Service/Schnittstellen/AVM_TR-064_first_steps.pdf)
  * [TR-064 Technical Report DSL Forum](http://www.broadband-forum.org/technical/download/TR-064.pdf)


### License

[MIT](https://opensource.org/licenses/MIT)
Author: Klaus Bremer


### Contributers

Many thanks for contributions, bugfixes or issue-reporting to:

* [Philipp Klaus](https://bitbucket.org/pklaus)
* [malleYay](https://bitbucket.org/malleYay)
* [Thomas Westfeld](https://bitbucket.org/westfeld)
* [Christian Fetzer](https://bitbucket.org/fetzerch)

