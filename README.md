## fritzconnection

Python-Tool to communicate with the AVM FritzBox.
Uses the TR-064 protocol.

### Dependencies

You need to get the python modules `lxml` and `requests` in order to use the tools:

    pip install lxml requests

### Available Modules, Commands and Tools

`fritzconnection.py` makes the SOAP interface of the FRITZ!Box available on the command line.
Shows all available services and actions when run with the argument `-c`.

`fritzstatus.py` is a command line interface to display status information of the FRITZ!Box.
It also serves as an example on how to use the fritzconnection module.

`fritzmonitor.py` is a Tkinter GUI to display current IP as well as the upstream and downstream rates.
It also makes it easy to reconnect and thus get a different IP from your ISP.

### Other Files

`fritztools.py` contains some helper functions and `test.py` contains unit tests.

### Resources

* [The Source Code of fritzconnection](https://bitbucket.org/kbr/fritzconnection)
* Information on TR-064:
  * [AVM's manual First Steps with TR-064](http://www.avm.de/de/Extern/files/tr-064/AVM_TR-064_first_steps.pdf)
  * [TR-064 Technical Report DSL Forum](http://www.broadband-forum.org/technical/download/TR-064.pdf)

