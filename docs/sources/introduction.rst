

Introduction
============

Technically the communication with the Fritz!Box works by UPnP using SCPD and SOAP for information transfer which is based on the TR-064 protocol. The TR-064 protocol uses the concepts of ``services`` and ``actions``. A service is a collection of actions for a given topic like WLAN-connections, registered hosts, phone calls, home-automation tasks and so on.

The documentation about all services and actions is available from the vendor AVM (see `Further Reading <further_reading.html>`_).

FritzConnection manages the inspection of a given Fritz!Box and can access all available services and corresponding actions. For some services it is required to provide the user-password for the box. The set of available services and actions may vary by router models and the installed Fritz!OS version.

The installation of fritzconnection (using pip) will also install a command line tool for the Fritz!Box api-inspection. The next sections will give an introduction to this command line tool and how to write modules on top of fritzconnection.

.. note::
    To use the TR-064 interface of the Fritz!Box, the settings for `Allow access for applications` and `Transmit status information over UPnP` in the `Home Network` -> `Network` -> `Network Settings` menu have to be activated. 


Internal defaults
-----------------

To access the router in a local network, fritzconnection use some default values: ::

    FRITZ_IP_ADDRESS = '169.254.1.1'
    FRITZ_TCP_PORT = 49000
    FRITZ_TLS_PORT = 49443
    FRITZ_USERNAME = 'dslf-config'

The ip-adress is a fallback-value common to every fritzbox-router, regardless of the individual configuration. In case of more than a single router in the local network (i.e. multiple Fritz!Boxes building a Mesh or connected by LAN building multiple WLAN access-points) the option ``-i`` (for the command line) or the keyword-parameter ``address`` (module usage) is required to address the router, otherwise it is not defined which one of the devices will respond.


Usernames and passwords
-----------------------

For some operations a username and/or a password is required. This can be given on the command line as parameters or, by using a module, as arguments. To not present these informations in clear text, username and password can get stored in the environment variables ``FRITZ_USERNAME`` and ``FRITZ_PASSWORD``. FritzConnection will check for these environment variables first and, if set, will use the corresponding values. 


Command line inspection
-----------------------

Installing fritzconnection by pip will also install the command line tool ``fritzconnection`` to inspect the Fritz!Box-API. With the option ``-h`` this will show a help menu: ::

    $ fritzconnection -h

    FritzConnection v1.3.0
    usage: fritzconnection [-h] [-i [ADDRESS]] [--port [PORT]] [-u [USERNAME]]
                           [-p [PASSWORD]] [-r] [-s] [-S SERVICEACTIONS]
                           [-a SERVICEARGUMENTS]
                           [-A ACTIONARGUMENTS ACTIONARGUMENTS] [-c [COMPLETE]]
                           [-e [ENCRYPT]]

    Fritz!Box API Inspection:

    optional arguments:
      -h, --help            show this help message and exit
      -i [ADDRESS], --ip-address [ADDRESS]
                            Specify ip-address of the FritzBox to connect
                            to.Default: 169.254.1.1
      --port [PORT]         Port of the FritzBox to connect to. Default: 49000
      -u [USERNAME], --username [USERNAME]
                            Fritzbox authentication username
      -p [PASSWORD], --password [PASSWORD]
                            Fritzbox authentication password
      -r, --reconnect       Reconnect and get a new ip
      -s, --services        List all available services
      -S SERVICEACTIONS, --serviceactions SERVICEACTIONS
                            List actions for the given service: <service>
      -a SERVICEARGUMENTS, --servicearguments SERVICEARGUMENTS
                            List arguments for the actions of a specified service:
                            <service>.
      -A ACTIONARGUMENTS ACTIONARGUMENTS, --actionarguments ACTIONARGUMENTS ACTIONARGUMENTS
                            List arguments for the given action of a specified
                            service: <service> <action>. Lists also direction and
                            data type of the arguments.
      -c [COMPLETE], --complete [COMPLETE]
                            List the complete api of the router
      -e [ENCRYPT], --encrypt [ENCRYPT]
                            use secure connection


With the option ``-s`` all available ``services`` are listed. If there are multiple fritz devices in the network, it is undefined which one will respond. In this case an additional parameter for the router ip must be given with the ``-i`` option (newer router models use ``192.168.178.1`` as factory setting). The number of services can vary depending on the router model: ::

    $ fritzconnection -s -i 192.168.178.1

    FritzConnection v1.3.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.12
    Servicenames:
                        any1
                        WANCommonIFC1
                        WANDSLLinkC1
                        WANIPConn1
                        WANIPv6Firewall1
                        DeviceInfo1
                        DeviceConfig1
                        Layer3Forwarding1
                        ...
                        X_AVM-DE_OnTel1
                        X_AVM-DE_Dect1
                        ...
                        WLANConfiguration1
                        WLANConfiguration2
                        WLANConfiguration3
                        ...
                        WANPPPConnection1
                        WANIPConnection1


Services starting with "X_AVM" are not covered by the TR-064 standard but are AVM-specific extensions.

All service-names are ending with a numeric value. In case a service is listed more than once the numeric value allows to select a specific one. Most prominent example is the WLANConfiguration service for accessing the 2.4 GHz and 5 GHz bands as well as the guest-network (given that the router-model provides these services).


Services and actions
....................

Every ``service`` has a set of corresponding ``actions``. The actions are listed by the flag ``-S`` with the servicename as parameter.  ::

    $ fritzconnection -i 192.168.178.1 -S WANIPConnection1

    FritzConnection v1.3.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.12

    Servicename:        WANIPConnection1
    Actionnames:
                        GetInfo
                        GetConnectionTypeInfo
                        SetConnectionType
                        GetStatusInfo
                        GetNATRSIPStatus
                        SetConnectionTrigger
                        ForceTermination
                        RequestConnection
                        GetGenericPortMappingEntry
                        GetSpecificPortMappingEntry
                        AddPortMapping
                        DeletePortMapping
                        GetExternalIPAddress
                        X_GetDNSServers
                        GetPortMappingNumberOfEntries
                        SetRouteProtocolRx
                        SetIdleDisconnectTime


A list of all available actions with their corresponding ``arguments`` is reported by the flag ``-a`` with the servicename as parameter: ::

    $ fritzconnection -i 192.168.178.1 -a WANIPConnection1

This can return a lengthy output. So the arguments for a single action of a given service can also get listed with the option ``-A`` and the service- and actionname as arguments. For example the output for the service ``WANIPConnection1`` and the action ``GetInfo`` will be: ::

    $ $ fritzconnection -i 192.168.178.1 -A WANIPConnection1 GetInfo

    FritzConnection v1.3.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.12

    Service:            WANIPConnection1
    Action:             GetInfo
    Parameters:

        Name                          direction     data type

        NewEnable                        out ->     boolean
        NewConnectionStatus              out ->     string
        NewPossibleConnectionTypes       out ->     string
        NewConnectionType                out ->     string
        NewName                          out ->     string
        NewUptime                        out ->     ui4
        NewLastConnectionError           out ->     string
        NewRSIPAvailable                 out ->     boolean
        NewNATEnabled                    out ->     boolean
        NewExternalIPAddress             out ->     string
        NewDNSServers                    out ->     string
        NewMACAddress                    out ->     string
        NewConnectionTrigger             out ->     string
        NewRouteProtocolRx               out ->     string
        NewDNSEnabled                    out ->     boolean
        NewDNSOverrideAllowed            out ->     boolean


For every action all arguments are listed with their name, direction and type. (Some arguments for other services may have the direction "in" for sending data to the router.)

The API of a FRITZ!Box depends on the model and the installed FRITZ!OS version. To report the complete api of the router, the option ``-c`` can be used: ::

    $ fritzconnection -i 192.168.178.1 -c > api.txt

In the above example the output is redirected to a file, because the output will be really huge.


Module usage
------------

FritzConnection works by calling actions on services and can send and receive action-arguments. A simple example is to reconnect the router with the provider to get a new external ip: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection()  #1
    fc.call_action('WANIPConnection1', 'ForceTermination')

At first an instance of FritzConnection must be created (*#1*). There can be a short delay doing this because fritzconnection has to wait for the response of the router to inspect the router-specific api.

The method ``call_action`` takes two required arguments: the service- and the action-name as strings. In case that a service or action is unknown (because of a typo or incompatible router model) fritzconnection will raise a ``FritzServiceError``. If the service is known, but not the action, then a ``FritzActionError`` gets raised.

.. note ::
    Once a FritzConnection instance has been created, it can be reused for all future call_action calls. Because instantiation is expensive (doing a lot of i/o for API inspection) this can increase performance significantly.


Let's look at another example using an address ``192.168.178.1`` and calling an action ``GetInfo`` on a service ``WLANConfiguration`` that requires a password: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.178.1', password='the_password')
    state = fc.call_action('WLANConfiguration1', 'GetInfo')

Calling the service ``WLANConfiguration1`` without giving a password (or providing a wrong one) will raise a ``FritzConnectionException``. Inspecting the API works without a password, but most of the API-calls require a password.

In case that the servicename is given without a numeric extension (i.e '1') fritzconnection adds the extension '1' by default. So ``WLANConfiguration`` becomes ``WLANConfiguration1``. The extension is required if there are multiple services with the same name. For backward compatibility servicenames like ``WLANConfiguration:1`` are also accepted.

The result of calling the ``call_action`` method is always a dictionary with the ``argument`` names as keys. The values are the output-arguments from the Fritz!Box. In the above example 'state' will be something like this: ::

    {'NewAllowedCharsPSK': '0123456789ABCDEFabcdef',
     'NewAllowedCharsSSID': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
                            '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
     'NewBSSID': '98:9B:CB:2B:93:B3',
     'NewBasicAuthenticationMode': 'None',
     'NewBasicEncryptionModes': 'None',
     'NewBeaconType': '11i',
     'NewChannel': 6,
     'NewEnable': True,
     'NewMACAddressControlEnabled': False,
     'NewMaxBitRate': 'Auto',
     'NewMaxCharsPSK': 64,
     'NewMaxCharsSSID': 32,
     'NewMinCharsPSK': 64,
     'NewMinCharsSSID': 1,
     'NewSSID': 'the WLAN name',
     'NewStandard': 'n',
     'NewStatus': 'Up'}

These informations are showing a lot of details about the WLAN configuration. In this example the network is up and operating on channel 6.

To activate or deactivate a network, the action ``SetEnable`` can get called. Inspection gives informations about the required arguments: ::

    $ $ fritzconnection -i 192.168.178.1 -A WLANConfiguration1 SetEnable

    FritzConnection v1.3.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.12

    Service:            WLANConfiguration1
    Action:             SetEnable
    Parameters:

        Name                          direction     data type

        NewEnable                     -> in         boolean


Here just one argument is listed for the in-direction. That means that this argument has to be send to the router. FritzConnection takes arguments as keyword-parameters for the ``call_action``-method: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.178.1', password='the_password')
    fc.call_action('WLANConfiguration1', 'SetEnable', NewEnable=False)

This call will deactivate the network (keep in mind: don't deactivate a wireless network by not having a backup cable connection). As there are no arguments listed for the out-direction, ``call_action`` will return an empty dictionary without any out-argument keys.

The ``call_action`` method also accepts a keyword-only argument with the name ``arguments`` that must be a dictionary with all input-parameters as key-value pairs (*new since 1.0*). Arguments like ``NewEnable`` can accept Python booleans instead of the numeric values [0, 1] (*new since 1.3*).

This is convenient for calls with multiple arguments for the in-direction, or for argument names not suitable as keyword parameters (like having a dash in the name) : ::

    arguments = {'NewEnable': 0}
    fc.call_action('WLANConfiguration1', 'SetEnable', arguments=arguments)


.. note ::
    Even if the router reports that a service exists, calling actions on this service may raise FritzActionErrors in case that the service is not in use. 



Example: Writing a module
.........................

Let's write a simple module using fritzconnection to report the WLAN status of a router: ::

    from itertools import count

    from fritzconnection import FritzConnection
    from fritzconnection.core.exceptions import FritzServiceError


    def get_wlan_status(fc):
        status = []
        action = 'GetInfo'
        for n in count(1):
            service = f'WLANConfiguration{n}'
            try:
                result = fc.call_action(service, action)
            except FritzServiceError:
                break
            status.append((service, result))
        return status


    def get_compact_wlan_status(fc):
        keys = ('NewSSID', 'NewChannel', 'NewStatus')
        return [
            (service, {key[3:]: status[key] for key in keys})
            for service, status in get_wlan_status(fc)
        ]


    def main(address, password):
        fc = FritzConnection(address=address, password=password)
        for service, status in get_compact_wlan_status(fc):
            print(f'{service}: {status}')


    if __name__ == '__main__':
        main(address='192.168.178.1', password='the_password')


Depending on the settings this will give an output like this: ::

    WLANConfiguration1: {'SSID': 'the_wlan_name', 'Channel': 6, 'Status': 'Up'}
    WLANConfiguration2: {'SSID': 'the_wlan_name', 'Channel': 100, 'Status': 'Up'}
    WLANConfiguration3: {'SSID': 'FRITZ!Box Gastzugang', 'Channel': 6, 'Status': 'Disabled'}


The modules in the fritzconnection library (modules in the lib-folder) can be used as code-examples of how to use fritzconnection.


Exceptions
----------

FritzConnection can raise several exceptions. For example using a service not provided by a specific router model will raise a ``FritzServiceError``. This and all other errors are defined in ``fritzconnection.core.exceptions`` and can get imported from this module (i.e. the ``FritzServiceError``): ::

    from fritzconnection.core.exceptions import FritzServiceError


.. include:: exceptions_hierarchy.rst


All exceptions are inherited from ``FritzConnectionException``. ``FritzServiceError`` and ``FritzActionError`` are superseding the older ``ServiceError`` and ``ActionError`` exceptions, that are still existing for backward compatibility. These exceptions are raised by calling unknown services and actions. All other exceptions are raised according to errors reported from the router. ``FritzLookUpError`` and ``FritzArrayIndexError`` are conceptually the same as a Python ``KeyError`` or ``IndexError``. Because of this they are also inherited from these Exceptions.


TLS-Encryption
--------------

FritzConnection supports encrypted communication with Fritz!Box devices by providing the option ``use_tls`` (*new in 1.2.0*): ::

    fc = FritzConnection(address=192.168.178.1, password=<password>, use_tls=True)

The default setting for ``use_tls`` is ``False``. For the command line tools encryption is provided by the flag ``-e`` or ``--encrypt``.


.. note ::
    - Using TLS will slow down the communication with the router. Especially getting a new FritzConnection instance will take longer by setting ``use_tls=True``. Hint: reuse instances.
    - Since the router uses a self-signed certificate, currently certificate-verification is disabled.
    - In case the client communicates with the router by WLAN and WPA is enabled, the communication is already encrypted.
    - In case the client communicates by VPN there is also no need to add an additional encryption layer.
    - The Fritz!Box backend allows to download the self signed certificate and to upload your own certificates: "Internet->Freigaben->FRITZ!Box-Dienste".
