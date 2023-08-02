
# fritzconnection

![](https://img.shields.io/pypi/pyversions/fritzconnection.svg)
![](https://img.shields.io/pypi/l/fritzconnection.svg)

Python-Interface to communicate with the AVM Fritz!Box. Supports the TR-064 protocol, the (AHA-)HTTP-Interface and also allows call-monitoring.


## Installation

For installation use pip:

```
    $ pip install fritzconnection
      or
    $ pip install fritzconnection[qr]
```

The latter will install the [segno](https://github.com/heuer/segno) package to enable QR-code creation for wifi login.

## Quickstart

Using fritzconnection is as easy as:

```
    from fritzconnection import FritzConnection

    fc = FritzConnection(address="192.168.178.1", user="user", password="pw")
    print(fc)  # print router model information

    # tr-064 interface: reconnect for a new ip
    fc.call_action("WANIPConn1", "ForceTermination")

    # http interface: gets history data from a device with given 'ain'
    fc.call_http("getbasicdevicestats", "12345 7891011")
```

FritzConnection provides two basic commands to communicate with the router APIs: `call_action()` for the __TR-064-Interface__ and `call_http()` for the __(AHA)-HTTP-Interface__. Both APIs can be used on the same FritzConnection instance side by side.

### call_action

`call_action()` expects a __TR-064__ service- and an action-name (and optional arguments). In general FritzConnection can execute every service and action provided by the (model-specific) API as documented by AVM. For i.e. this can be network settings, status informations, access to home automation devices and much more. The `call_action()` method returns the response from the router as a dictionary with the values already converted to the matching Python datatypes.

### call_http

`call_http()` expects a command for the __http-interface__ like "getbasicdevicestats" and, depending on the command, additional arguments like a device "ain" (identifier). A call to the method returns a dictionary with the `content-type`, the `encoding` and the `response` data of the http-response. The content-type of the response-data is typical "text/plain" or "text/xml" and may need further processing.

### Username and password

To avoid hardcoding the arguments `user` and `password` in applications FritzConnection can read both from the environment variables `FRITZ_USERNAME` and `FRITZ_PASSWORD`.


### Caching

On instanciation FritzConnection has to inspect the model-specific router-API. This causes a lot of network requests and can take some seconds. To avoid this FritzConnection provides a cache that can get activated by the `use_cache` parameter:

```
    fc = FritzConnection(..., use_cache=True)
```

This argument defaults to `False`. After creating the cache FritzConnection will start up much more faster.


## Library


The package comes with library-modules to make some API calls easier and also demonstrates how to implement applications on top of FritzConnection.


## Documentation

The full documentation and release notes are at [https://fritzconnection.readthedocs.org](https://fritzconnection.readthedocs.org)

