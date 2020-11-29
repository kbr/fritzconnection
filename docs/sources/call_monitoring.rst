
Call Monitoring
---------------

The fritzmonitor-module is a core module of fritzconnection to provide real-time informations about incoming and outgoing phone-calls. This functionality is based on a separate socket-connection to the router and does not communicate by TR-064. 

FritzMonitor provides a queue of type ``queue.Queue`` for accessing CallMonitor events. To check the events send from the router, fritzconnection comes with a ``fritzmonitor`` command line tool. The next block shows a typical session: ::

    $ fritzmonitor -i 192.168.178.1

    fritzconnection v1.4.0
    start fritzmonitor on address: 192.168.178.1
    settings for socket-timeout: 10 [sec]
    settings for healthcheck-timeout: 10 [sec]
    start listening for events (to stop press ^C, for stopping reaction time may be up to socket-timeout):

    28.11.20 15:17:43;RING;2;12345;6789;SIP0;
    28.11.20 15:17:47;CONNECT;2;4;6789;
    28.11.20 15:17:50;DISCONNECT;2;4;
    ...

The events are of type ``string`` in a format defined by AVM.
The option ``-i`` specifies the ip address of the router. The option ``-h`` provides a help menu. 

Here is a basic example how to use FritzMonitor in a module to pull events: ::

    from fritzconnection.core.fritzmonitor import FritzMonitor

    def process_events(monitor, event_queue, healthcheck_interval=10):
        while True:
            try:
                event = event_queue.get(timeout=healthcheck_interval)
            except queue.Empty:
                # check health:
                if not monitor.is_alive:
                    raise OSError("Error: fritzmonitor connection failed")
            else:
                # do event processing here:
                print(event)

    def main():
        """Entry point: example to use FritzMonitor.
        """
        try:
            # as a context manager FritzMonitor will shut down the monitor thread
            with FritzMonitor(address='192.168.178.1') as monitor:
                event_queue = monitor.start()
                process_events(monitor, event_queue)
        except (OSError, KeyboardInterrupt) as err:
            print(err)

    if __name__ == "__main__":
        main()


The FritzMonitor API is also documented in `Structure and API <api.html>`_.


.. note ::
    To do call monitoring, the CallMonitor service of the Fritz!Box has to be activated.
    This can be done with any registered phone by typing the following codes: ::

        activate: #96*5*
        deactivate: #96*4*


