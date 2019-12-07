

FritzConnection
===============

This is the fritzconnection core module – it manages the inspection of a given Fritz!Box and can access all services and corresponding actions. For some services it is required to provide the user-password for the box. Avaliable services and actions may vary by router models. Also vendor branded models may have modified service sets.

All other modules in the package are not required to run fritzconnection but are there for convenience and as examples how to build new modules using the fritzconnection module.

The next sections will show how to inspect and use the API of a given router.


Internal defaults
-----------------

To access the router in the local network, fritzconnection use some default values: ::

    FRITZ_IP_ADDRESS = '169.254.1.1'
    FRITZ_TCP_PORT = 49000
    FRITZ_USERNAME = 'dslf-config'

The ip-adress is a fallback-value common to every fritzbox-router, regardless of the individual configuration. In case of more than a single box in the local network (i.e. multi Fritz!Boxes connected by LAN building multiple WLAN access-points) the option ``-i`` (for the command line) or the keyword-parameter ``address`` (using as a module) is neccessary to address one of the routers, otherwise it is not defined which of the routers will response.



Command line usage
------------------

Given that the file ``fritzconnection.py`` is in the path a call with the option ``-h`` will show a help menu: ::

    $ python fritzconnection.py -h
    usage: fritzconnection.py [-h] [-i [ADDRESS]] [--port [PORT]] [-u USERNAME]
                              [-p PASSWORD] [-r] [-s] [-S SERVICEACTIONS]
                              [-a SERVICEARGUMENTS]
                              [-A ACTIONARGUMENTS ACTIONARGUMENTS] [-c]

    FritzBox API

    optional arguments:
      -h, --help            show this help message and exit
      -i [ADDRESS], --ip-address [ADDRESS]
                            Specify ip-address of the FritzBox to connect
                            to.Default: 169.254.1.1
      --port [PORT]         Port of the FritzBox to connect to. Default: 49000
      -u USERNAME, --username USERNAME
                            Fritzbox authentication username
      -p PASSWORD, --password PASSWORD
                            Fritzbox authentication password
      -r, --reconnect       Reconnect and get a new ip
      -s, --services        List all available services
      -S SERVICEACTIONS, --serviceactions SERVICEACTIONS
                            List actions for the given service: <service>
      -a SERVICEARGUMENTS, --servicearguments SERVICEARGUMENTS
                            List arguments for the actions of aspecified service:
                            <service>.
      -A ACTIONARGUMENTS ACTIONARGUMENTS, --actionarguments ACTIONARGUMENTS ACTIONARGUMENTS
                            List arguments for the given action of aspecified
                            service: <service> <action>.
      -c, --complete        List all services with actionnames and arguments.


With the option ``-s`` all services available without a password are listed: ::

    $ python fritzconnection.py -s

    FritzConnection:
    version:            0.6
    model:              FRITZ!Box Fon WLAN 7390
    Servicenames:
                        Any:1
                        WANCommonInterfaceConfig:1
                        WANDSLLinkConfig:1
                        WANIPConnection:1
                        WANIPv6FirewallControl:1


With a given password more services are listed. The number of services can vary depending on the router model: ::


    $ python fritzconnection.py -p <the password> -s

    FritzConnection:
    version:            0.6
    model:              FRITZ!Box Fon WLAN 7390
    Servicenames:
                        Any:1
                        DeviceConfig:1
                        DeviceInfo:1
                        Hosts:1
                        LANConfigSecurity:1
                        LANEthernetInterfaceConfig:1
                        ...
                        WLANConfiguration:1
                        WLANConfiguration:2
                        WLANConfiguration:3
                        ...
                        X_AVM-DE_UPnP:1
                        X_AVM-DE_WebDAVClient:1

Services starting with "X_AVM" are not covered by the TR-064 standard but are AVM-specific extensions.

All service-names are ending with a colon and a numeric value. In case a service is listed more than once the numeric value allows to select a specific one.


Services and actions
....................

Every ``service`` has a set of corresponding ``actions``. A list of all available ``actions`` with their corresponding ``arguments`` is reported by the flag ``-a`` with the ``service`` as parameter: ::

    $ python fritzconnection.py -p <the password> -a WANIPConnection:1

This can return a lengthy output. So the ``arguments`` for a single ``action`` of a given ``service`` can get listed with the option ``-A`` and the ``service`` and ``action`` as arguments. For example the output for the service "WANIPConnection:1" and the action "GetInfo" will be: ::

    $ python fritzconnection.py -p <the password> -A WANIPConnection:1 GetInfo

    FritzConnection:
    version:            0.6
    model:              FRITZ!Box Fon WLAN 7390

    Servicename:        WANIPConnection:1
    Actionname:         GetInfo
    Arguments:
                        ('NewConnectionStatus', 'out', 'string')
                        ('NewConnectionTrigger', 'out', 'string')
                        ('NewConnectionType', 'out', 'string')
                        ('NewDNSEnabled', 'out', 'boolean')
                        ('NewDNSOverrideAllowed', 'out', 'boolean')
                        ('NewDNSServers', 'out', 'string')
                        ('NewEnable', 'out', 'boolean')
                        ('NewExternalIPAddress', 'out', 'string')
                        ('NewLastConnectionError', 'out', 'string')
                        ('NewMACAddress', 'out', 'string')
                        ('NewNATEnabled', 'out', 'boolean')
                        ('NewName', 'out', 'string')
                        ('NewPossibleConnectionTypes', 'out', 'string')
                        ('NewRSIPAvailable', 'out', 'boolean')
                        ('NewRouteProtocolRx', 'out', 'string')
                        ('NewUptime', 'out', 'ui4')


For every ``action`` all ``arguments`` are listed with their name, direction and type. (Some arguments have the direction "in" for sending data to the router.)

The command line mode of fritzconnection can report all available ``services`` and corresponding ``actions`` with the according ``arguments`` for a given router model. The option ``-c`` lists the complete API at once (can get *really* lengthy).


Module usage
------------

The TR-064 protocol is based on services and actions. A service is a collection of actions for a given topic like WAN-connection, registered hosts and so on.

fritzconnection works by calling actions on services and can send and receive action-arguments.

A simple example is to reconnect the router with the provider to get a new external ip: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection()  #1
    fc.call_action('WANIPConnection', 'ForceTermination')

At first an instance of FritzConnection must be created (#1). There can be a short delay doing this because fritzconnection has to wait for the response of the router to inspect the router-specific api. Reusing the instance later on will increase performance.

The method ``call_action`` takes the two required arguments: the service- and action-name as strings. In case that a service or action is unknown (because of a typo or incompatible router model) fritzconnection will raise a ``ServiceError`` or an ``ActionError``.

This is an example for a call that does something, but takes no action-arguments and returns no result. For reconnection there is also a buildin shortcut in fritzconnection: ::

    fc.reconnect()

Let's look at an example using an address ('192.168.1.1') and calling an action ('GetInfo') on a service ('WLANConfiguration') that requires a password: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.1.1', password='the_password')
    state = fc.call_action('WLANConfiguration', 'GetInfo')

Calling the service 'WLANConfiguration' without giving a password to FritzConnection will raise a ``ServiceError``. In case that the servicename is missing the numeric extension (i.e ``:1``) fritzconnection adds the extension ':1' by default. The extension is required if there are multiple services with the same name. This can be the case for the *WLANConfigurations* if the router supports 2.4 GHz and 5GHz and may be a separate Guest-Network.

In following example the call will return a result. The result is always a dictionary with all action arguments as keys. According to the inspection information for the action *GetInfo* of the service *WLANConfiguration:1*: ::

    $ python fritzconnection.py -p <the password> -A WLANConfiguration:1 GetInfo

    FritzConnection:
    version:            0.6
    model:              FRITZ!Box Fon WLAN 7390

    Servicename:        WLANConfiguration:1
    Actionname:         GetInfo
    Arguments:
                        ('NewAllowedCharsPSK', 'out', 'string')
                        ('NewAllowedCharsSSID', 'out', 'string')
                        ('NewBSSID', 'out', 'string')
                        ('NewBasicAuthenticationMode', 'out', 'string')
                        ('NewBasicEncryptionModes', 'out', 'string')
                        ('NewBeaconType', 'out', 'string')
                        ('NewChannel', 'out', 'ui1')
                        ('NewEnable', 'out', 'boolean')
                        ('NewMACAddressControlEnabled', 'out', 'boolean')
                        ('NewMaxBitRate', 'out', 'string')
                        ('NewMaxCharsPSK', 'out', 'ui1')
                        ('NewMaxCharsSSID', 'out', 'ui1')
                        ('NewMinCharsPSK', 'out', 'ui1')
                        ('NewMinCharsSSID', 'out', 'ui1')
                        ('NewSSID', 'out', 'string')
                        ('NewStandard', 'out', 'string')
                        ('NewStatus', 'out', 'string')

the result 'state' is a dictionary with the values: ::

    {'NewAllowedCharsPSK': '0123456789ABCDEFabcdef',
     'NewAllowedCharsSSID': '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz '
                            '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~',
     'NewBSSID': 'XX:YY:A6:16:70:5E',
     'NewBasicAuthenticationMode': 'None',
     'NewBasicEncryptionModes': 'None',
     'NewBeaconType': '11i',
     'NewChannel': 2,
     'NewEnable': '1',
     'NewMACAddressControlEnabled': '0',
     'NewMaxBitRate': 'Auto',
     'NewMaxCharsPSK': 64,
     'NewMaxCharsSSID': 32,
     'NewMinCharsPSK': 64,
     'NewMinCharsSSID': 1,
     'NewSSID': 'your wlan name',
     'NewStandard': 'n',
     'NewStatus': 'Up'}

In this case the WLAN network is up and operating on channel 2. To activate or deactivate the network the action 'SetEnable' can get called. Inspection gives the information about the required arguments: ::

    $ python fritzconnection.py -p the_password -A WLANConfiguration:1 SetEnable
    ...
    Servicename:        WLANConfiguration:1
    Actionname:         SetEnable
    Arguments:
                        ('NewEnable', 'in', 'boolean')

Here just one argument is listed for the 'in'-direction. That means that this argument has to be send to the router. fritzconnection sends arguments by giving them as keyword-parameters to the 'call_action'-method: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.1.1', password='the_password')
    fc.call_action('WLANConfiguration:1', 'SetEnable', NewEnable=0)

This call will deactivate the network. As there are no arguments listed for the 'out'-direction, the call will return no result.


Example: Writing a module
.........................

Let's write a simple example for a module using fritzconnection to report the WLAN status of a router: ::

    from itertools import count

    from fritzconnection import (
        FritzConnection,
        ServiceError
    )


    def get_wlan_status(fc):
        status = []
        action = 'GetInfo'
        for n in count(1):
            service = 'WLANConfiguration:{}'.format(n)
            try:
                status.append(fc.call_action(service, action))
            except ServiceError:
                break
        return status


    def get_compact_wlan_status(fc):
        keys = ('NewSSID', 'NewChannel', 'NewStatus')
        return [
            {key[3:]: status[key] for key in keys}
            for status in get_wlan_status(fc)
        ]


    def main(address, password):
        fc = FritzConnection(address=address, password=password)
        return get_compact_wlan_status(fc)


    if __name__ == '__main__':
        from pprint import pprint
        pprint(main(address='192.168.1.1', password='the_password'))

Depending on the settings this will result in an output like this: ::

    [{'Channel': 2, 'SSID': 'your wlan name', 'Status': 'Up'},
     {'Channel': 40, 'SSID': 'your wlan name', 'Status': 'Up'},
     {'Channel': 2, 'SSID': 'FRITZ!Box guest access', 'Status': 'Disabled'}]

The modules in the fritzconnection library provide some of these functionalities and can be used as code-examples of how to use fritzconnection-module.

