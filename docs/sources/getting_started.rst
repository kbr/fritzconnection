

Getting Started
===============

The Fritz!Box provides several protocols for external applications to interact with the router. FritzConnection makes use of the TR-064 protocol and the HTTP-Interface. Both APIs can be used on a single instance of FritzConnection side by side.

The documentation about all services and actions for the TR-064 protocol and also the available commands for the http-interface is available from the vendor AVM (see `Further Reading <further_reading.html>`_).

.. note::
    To use the TR-064 interface of the Fritz!Box, the settings for `Allow access for applications` and `Transmit status information over UPnP` in the `Home Network` -> `Network` -> `Network Settings` menu have to be activated.

    To access the http-interface the router must be configured with a user and a password.


Default IP-Address
------------------

To access the router in a local network, fritzconnection uses a default ip-address: ::

    FRITZ_IP_ADDRESS = '169.254.1.1'

This ip-adress is a fallback-address common to every fritzbox-router and repeater, regardless of the individual configuration. If there are multiple devices in the local network, i.e. for building a Mesh, then it is necessary to provide the ip for the requested device, either at the command line with the option :command:`-i` or the keyword-argument `address` for module usage. Otherwise it is not defined which device will respond.


Username and password
---------------------

For some TR-064 operations and for all http-interface commands a username and/or a password is required. This can be given on the command line as parameters or, by using a module, as arguments. To not present these information in clear text or in the program code, username and password can get stored in the **environment variables** ``FRITZ_USERNAME`` and ``FRITZ_PASSWORD``. If FritzConnection doesn't get the username or password as arguments, then it will check for these environment variables and, if set, will use the corresponding values.

For Fritz!OS < 7.24 the username was optional. For newer versions an individual username is required. If a username is not provided, fritzconnection will try to find the username of the last logged in user from the Fritz!Box and will use this username (as AVM recommends for systems >= 7.24).


The TR-064 API
--------------

The TR-064 protocol uses the concept of ``services`` and ``actions``. A service is a collection of actions for a given topic like WLAN-connections, registered hosts, phone calls, home-automation tasks and so on. An action can have optional ``arguments`` for sending and receiving data. The set of available services and actions may vary by router models and the installed Fritz!OS version.

Installing fritzconnection by pip will also install the command line tool `fritzconnection` to inspect the model-specific Fritz!Box TR-064 API. With the option :command:`-h` this will show a help menu: ::

    $ fritzconnection -h

    usage: fritzconnection [-h] [-i [ADDRESS]] [--port [PORT]] [-u [USERNAME]]
                           [-p [PASSWORD]] [-e [ENCRYPT]] [-x] [-y]
                           [--cache-format [CACHE_FORMAT]]
                           [--cache-directory [CACHE_DIRECTORY]] [-r] [-R] [-s]
                           [-S SERVICEACTIONS] [-a SERVICEARGUMENTS]
                           [-A ACTIONARGUMENTS ACTIONARGUMENTS] [-c [COMPLETE]]

    options:
      -h, --help            show this help message and exit
      -i [ADDRESS], --ip-address [ADDRESS]
                            Specify ip-address of the FritzBox to connect to.
                            Default: 169.254.1.1
      --port [PORT]         Port of the FritzBox to connect to. Default: 49000
      -u [USERNAME], --username [USERNAME]
                            Fritzbox authentication username
      -p [PASSWORD], --password [PASSWORD]
                            Fritzbox authentication password
      -e [ENCRYPT], --encrypt [ENCRYPT]
                            Flag: use secure connection (TLS)
      -x, --use-cache       Flag: use api cache
                            (speed-up subsequent instanciations)
      -y, --suppress-cache-verification
                            Flag: suppress cache verification, implies -x
      --cache-format [CACHE_FORMAT]
                            cache-file format: json|pickle (default: pickle)
      --cache-directory [CACHE_DIRECTORY]
                            path to cache directory (default: ~.fritzconnection)
      -r, --reconnect       Reconnect and get a new ip
      -R, --reboot          Reboot the router
      -s, --services        List all available services
      -S SERVICEACTIONS, --serviceactions SERVICEACTIONS
                            List actions for the given service: <service>
      -a SERVICEARGUMENTS, --servicearguments SERVICEARGUMENTS
                            List arguments for the actions of a specified
                            service:<service>.
      -A ACTIONARGUMENTS ACTIONARGUMENTS, --actionarguments
                            ACTIONARGUMENTS ACTIONARGUMENTS
                            List arguments for the given action of a specified
                            service: <service> <action>. Lists also direction
                            and data type of the arguments.
      -c [COMPLETE], --complete [COMPLETE]
                            List the complete api of the router


Services
........

With the option :command:`-s` all available ``services`` are listed. If there are multiple fritz-devices in the network, it is undefined which one will respond. In this case the router-ip must be given with the option :command:`-i`. The number of listed `services` can vary depending on the router model: ::

    $ fritzconnection -s -i 192.168.178.1

    fritzconnection v1.10.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.29
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


Services starting with `X_AVM` are not covered by the TR-064 standard but AVM-specific extensions.

All service-names are ending with a numeric value. In case a service is listed more than once the numeric value allows to select a specific one. Most prominent example is the WLANConfiguration service for accessing the 2.4 GHz and 5 GHz bands as well as the guest-network (given that the router-model provides these services).


Actions
.......

Every ``service`` has a set of corresponding ``actions``. The actions are listed by the flag :command:`-S` with the servicename as parameter.  ::

    $ fritzconnection -i 192.168.178.1 -S WANIPConnection1

    fritzconnection v1.10.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.29


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


Arguments
.........

An ``Action`` can have optional ``Arguments``. A list of all available actions with their corresponding arguments is reported by the flag :command:`-a` with the servicename as parameter: ::

    $ fritzconnection -i 192.168.178.1 -a WANIPConnection1

This can return a lengthy output. So the arguments for a specific action of a given service can get listed with the option :command:`-A` and the service- and actionname as arguments. For example the output for the service `WANIPConnection1` and the action `GetInfo` will be: ::

    $ fritzconnection -i 192.168.178.1 -A WANIPConnection1 GetInfo

    fritzconnection v1.10.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.29


    Service:            WANIPConnection1
    Action:             GetInfo
    Parameters:

        Name                                  direction     data type

        NewEnable                                out ->     boolean
        NewConnectionStatus                      out ->     string
        NewPossibleConnectionTypes               out ->     string
        NewConnectionType                        out ->     string
        NewName                                  out ->     string
        NewUptime                                out ->     ui4
        NewLastConnectionError                   out ->     string
        NewRSIPAvailable                         out ->     boolean
        NewNATEnabled                            out ->     boolean
        NewExternalIPAddress                     out ->     string
        NewDNSServers                            out ->     string
        NewMACAddress                            out ->     string
        NewConnectionTrigger                     out ->     string
        NewRouteProtocolRx                       out ->     string
        NewDNSEnabled                            out ->     boolean
        NewDNSOverrideAllowed                    out ->     boolean


For every action all, arguments are listed with their name, direction and type. (Some arguments for other services may have the direction "in" for sending data to the router.)

The API of a FRITZ!Box depends on the model and the installed FritzOS version. To report the complete API of the router, the option :command:`-c` can be used: ::

    $ fritzconnection -i 192.168.178.1 -c > api.txt

In the above example the output is redirected to the file `api.txt`, because the output will be really huge.


Module usage
............

FritzConnection works by calling actions on services and can send and receive arguments. A simple example is to reconnect the router with the provider to get a new external ip: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection()
    fc.call_action('WANIPConnection1', 'ForceTermination')

At first an instance of `FritzConnection` must be created. There can be a short delay doing this, because fritzconnection has to do a lot of communication with the router to get the router-specific API.

.. note ::
    A FritzConnection instance can be **reused** for all further `call_action()` calls (and also `call_http()` calls) **without side-effects**. For a single device (i.e. the router) an application needs just one instance. Because instanciation can be expensive (time consuming), having a single instance can save memory and speed up things.

    Update: with the introduction of the `api-cache` in version `1.10` instanciation is much more faster than before. However, reusing an instance is still a good idea.

The method `call_action` takes two required arguments: the service- and the action-name as strings. In case that a service is unknown (because of a typo or incompatible router model) fritzconnection will raise a `FritzServiceError`. If the service is known, but not the action, then a `FritzActionError` gets raised.


Let's look at another example using an address "192.168.178.1" for the action "GetInfo" on the service "WLANConfiguration" that requires a password: ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address="192.168.178.1", password="the_password")
    state = fc.call_action("WLANConfiguration1", "GetInfo")

Calling the service `WLANConfiguration1` without giving a password (or providing a wrong one) will raise a `FritzConnectionException`. Inspecting the API works without a password, but most of the other API-calls require one.

.. note ::
    The environment variables ``FRITZ_USERNAME`` and ``FRITZ_PASSWORD`` can be used to avoid hardcoding username and password.

In case that the servicename is given without a numeric extension (i.e '1') fritzconnection adds the extension '1' by default. So `WLANConfiguration` becomes `WLANConfiguration1`. The extension is required if there are multiple services with the same name. For backward compatibility servicenames like `WLANConfiguration:1` are also accepted.

If `call_action()` provides a result, the method returns a dictionary: the keys are corresponding to the `Argument name` as given in the AVM-documentation and the values are the data provided from the router. In the above example `state` will be something like this: ::

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

This information provides a lot of details about the WLAN configuration. In this example the network is up and operating on channel 6. If the values are numeric or boolean, ``call_action()`` returns the matching Python datatype.

To activate or deactivate a network, the action `SetEnable` can get called. Inspection gives information about the required arguments: ::

    $ fritzconnection -i 192.168.178.1 -A WLANConfiguration1 SetEnable

    fritzconnection v1.10.0
    FRITZ!Box 7590 at http://192.168.178.1
    FRITZ!OS: 7.29


    Service:            WLANConfiguration1
    Action:             SetEnable
    Parameters:

        Name                                  direction     data type

        NewEnable                             -> in         boolean


Here just one argument is listed for the in-direction. That means that this argument has to be send to the router. FritzConnection takes arguments as keyword-parameters for the `call_action`-method, where the keyword is set to the `argument name` (`NewEnable` in this case) : ::

    from fritzconnection import FritzConnection

    fc = FritzConnection(address='192.168.178.1', password='the_password')
    fc.call_action('WLANConfiguration1', 'SetEnable', NewEnable=False)

This call will deactivate the network (beware: don't deactivate a wireless network by not having a backup cable connection). As there are no arguments listed for the out-direction, `call_action` will return an empty dictionary.

In some cases it can happen that there is a dash in an argument-name. Then this argument-name is not usable as a keyword-parameter. Therefore the `call_action` method also accepts a keyword-only argument with the name `arguments` that must be a dictionary with all input-parameters as key-value pairs (*new in 1.0*): ::

    arguments = {'NewEnable': False}
    fc.call_action('WLANConfiguration1', 'SetEnable', arguments=arguments)

If `arguments` is given, the values of all further keyword-parameters are ignored; you can use just one way to provide arguments.

.. note ::
    Prior to version 1.3 booleans must be given as numeric values 1 and 0. Since version 1.3 `True` and `False` can get used.



Example: report the WLAN status
...............................

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


The HTTP API
------------

This interface (also known as AHA-HTTP-Interface) allows to interact with smart-home devices. The functionality partly overlap with the TR-064 interface, which provides a better performance. The interface works by sending a ``command`` with optional arguments like an ``identifier`` (aka ``ain``) as http-request and returns an http-response.

Commands are send by the method ``call_http()``. The http-response from this request is converted to a dictionary with the keys `content-type`, `encoding` and `content`. The values are typical "text/plain" or "text/xml" as `content-type`, "utf-8" as `encoding` and a string as `content` that may need further processing. This dictionary gets returned from the `call_http()` method.

Here is an example that selects all devices which are switches and report the temperature from these devices (assuming that all switches have temperature sensors). At first create a FritzConnection instance that can get reused (user and password are read from the environment): ::

    from fritzconnection.core.fritzconnection import FritzConnection
    fc = FritzConnection(address="192.168.178.1", use_cache=True)

Then implement the code using the http-interface to report all temperatures: ::

    result = fc.call_http("getswitchlist")
    switch_identifiers = result["content"].split(",")
    for identifier in switch_identifiers:
        result = fc.call_http("gettemperature", identifier.strip())
        temperature = float(result["content"]) * 0.1
        print(temperature)

The command "getswitchlist" returns a dictionary as result. The content is a string with a comma separated list of identifiers from devices which are switches. Then for every device `call_http()` gets called with the arguments "gettemperature" as `command` and the corresponding `identifier`. The result again is a dictionary with the temperature as `content`.

**The functionalities of the TR-064- and http-interface can overlap.** Here is how to do the same as above by means of the TR-064 API: ::

    from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation

    fh = FritzHomeAutomation(fc)
    # create a list of HomeAutomationDevice instances:
    devices = [d for d in fh.get_homeautomation_devices() if d.is_switchable]
    for device in devices:
        temperatur = device.TemperatureCelsius * 0.1
        print(temperature)

This example makes use of the fritzhomeauto library-module providing the `FritzHomeAutomation` and `HomeAutomationDevice` classes.

At first the instance of FritzConnection gets reused to initialize the FritzHomeAutomation instance 'fh'. On this instance the method `get_homeautomation_devices()` is called, returning a list of all homeautomation-devices known by the router, represented as HomeAutomationDevice-instances. On these instances the `is_switchable` property gets called to filter all devices which are switches. Then the example code iterates over the existing list of HomeAutomationDevice-instances to report the temperature that is already known by the instances and don't need additional calls to the API.

.. note::
    In general the TR-064 API is faster than the HTTP-API. Whether this is an issue depends on the application. However, for functionalities available by both APIs it makes more sense to use the TR-064 API.


Combining the APIs
------------------

For home-automation tasks it can make sense to combine both interfaces. Let's say that the temperature-history of all devices providing a temperature-sensor should get reported. The TR-064 API provides an efficient way to get all devices with energy-sensors and the http-interface provides a command to access the history-data. Again at first `fc` and `fh` are defined and can get reused later: ::

    from fritzconnection.core.fritzconnection import FritzConnection
    from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation

    fc = FritzConnection(address="192.168.178.1", use_cache=True)
    fh = FritzHomeAutomation(fc)

Then the devices are filtered by the property `is_energy_sensor` and are HomeAutomationDevice-instances. As the history of sensor-data is only provided by the http-interface the `call_http()` method is called with the appropriate command "getbasicdevicestats" and the "ain" of the device: ::

    devices = [d for d in fh.get_homeautomation_devices() if d.is_energy_sensor]
    for device in devices:
        # device.identifier provides the ain:
        response = fc.call_http("getbasicdevicestats", identifier=device.identifier)
        print(response)

The response is a dictionary with the `content` given as xml-data that needs further processing.

For this the `HomeAutomationDevice` class (defined in fritzconnection.lib.fritzhomeauto) already provides a method for xml-processing of the "getbasicdevicestats" xml-response: ::

    devices = [d for d in fh.get_homeautomation_devices() if d.is_energy_sensor]
    for device in devices:
        stats = device.get_basic_device_stats()
        temperatures = stats['temperature']['data']
        temperatures = list(map(lambda x: x * 0.1, temperatures))

The code is the same as before, but in the loop the method `get_basic_device_stats()` is called which returns a nested dictionary with the temperature data already extracted from the xml-data. The last line converts the temperatures from a sequence of strings to a list of floating point data (in ºC).

There is no restriction to use just ``call_action()`` or ``call_http()``. On a single FritzConnection instance both methods can get combined to best fit the needs.


Exceptions
----------

fritzconnection can raise several exceptions. For example using a service not provided by a specific router model will raise a `FritzServiceError`. This and all other errors are defined in `fritzconnection.core.exceptions` and can get imported from this module (i.e. the `FritzServiceError`): ::

    from fritzconnection.core.exceptions import FritzServiceError


.. include:: exceptions_hierarchy.rst


All exceptions are inherited from `FritzConnectionException`. `FritzServiceError` and `FritzActionError` are superseding the older `ServiceError` and `ActionError` exceptions (still existing for backward compatibility). These exceptions are raised by calling unknown services and actions. All other exceptions are raised according to errors reported from the router (mirroring FritzOS errors). `FritzLookUpError` and `FritzArrayIndexError` are conceptually the same as Pythons `KeyError` or `IndexError`. Because of this they are also inherited from these Exceptions.


API-Cache
---------

Stores the router api in an external file (*new in 1.10*). Loading the api-data from the router requires a lot of communication (many slow i/o) and can take up to several seconds. Reading the api-data from a single local file is much faster. The cache is activated by the `use_cache` argument: ::

    fc = FritzConnection(address=192.168.178.1, use_cache=True)

At first run the api gets loaded from the router and stored in a cache-file. On the next runs the api gets loaded from the cache-file. There is a separate cache-file for every ip-address, allowing to cache the api for mutiple devices.

With the argument `cache_directory` the location of the cache files can be specified. Default is the `~.fritzconnection` folder in the user home-directory on systems providing this default location.

.. note ::
    The default cache-format is `pickle`, which is compact, fast and can be considered safe as it is your own data. However, the `json` format is also supported. With the argument `cache_format` the format can set to `json`.

After loading the api from a cache-file, the data are verified to be still valid for the given router-model and the current installed software version. In case the cache is outdated, the api-data are reloaded from the router and the cache-file gets updated. The verifying step requires a request to the router, which can take some milliseconds. With the argument `verify_cache=False` verifying can turned off, loading the api even faster.

.. warning ::
    On deactivate verifying, the cache data may be outdated if something has changed on the router side. As a consequence these changes may not be visible for the fritzconnection library (Simple solution: turn verifying on or delete the cache-file.) However, chances are that one didn't mention this until strange things happen.

    Update: since version `1.11` cache verification is much faster than before, so there is no longer a real need to deactivate the cache verification.


TLS-Encryption
--------------

fritzconnection supports encrypted communication with Fritz!Box devices by providing the option `use_tls` (*new in 1.2*): ::

    fc = FritzConnection(address=192.168.178.1, password=<password>, use_tls=True)

The default setting for `use_tls` is `False`. For the command line tools encryption is provided by the flags :command:`-e` or :command:`--encrypt`. Encryption can be a useful option in a non-private LAN like a company-LAN.


.. note ::
    - Using TLS will slow down the communication with the router. Especially getting a new FritzConnection instance will take longer by setting `use_tls=True`. **Hint: reuse instances**.
    - Since the router uses a self-signed certificate, currently certificate-verification is disabled.
    - In case the client communicates with the router by WLAN and WPA is enabled, the communication is already encrypted.
    - In case the client communicates by VPN there is also no need to add an additional encryption layer.


Environment-Variables
---------------------

Some arguments given to `FritzConnection` can be stored in the environment. This has the advantage that arguments like `user` and `password` don't have to be provided as hardcoded arguments. The following environment variables are checked in case that a corresponding argument is missing:

- ``FRITZ_USERNAME`` – the username
- ``FRITZ_PASSWORD`` – the password
- ``FRITZ_USECACHE`` – `True` or `False` (default: `False`)
- ``FRITZ_CACHEFORMAT`` – `json` or `pickle` (default: `pickle`)
- ``FRITZ_CACHEDIRECTORY`` – the cache-directory path (default: `~.fritzconnection`)

The default-values are used if neither an argument is given to `fritzconnection()` nor an environment-variable is defined.

