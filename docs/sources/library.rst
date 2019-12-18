Library Modules
===============

The library is a package with modules on top of FritzConnection to address specific tasks. Also they can be used as examples on how to use FritzConnection.


FritzHomeAutomation
-------------------

Can access Homeautomation devices to read the current states and set the status of switches. Usage from the command line: ::

    $ fritzhomeauto -i 192.168.178.1 -p <password>
    FRITZ!Box 7590 at ip 192.168.178.1
    FRITZ!OS: 7.12
    Status of registered home-automation devices:

    Device Name             AIN                 Power[W]   t[°C]   switch
    FRITZ!DECT 210 #1       '11657 0240192'        0.000    23.5   on

The optional ``-v`` flag will give a verbose report about all device informations, including the settings of radiator controls.

The ``-s`` flag can set the state of switches. This flag requires two parameters: the device identifier (AIN) and the state to set [on|off]. The following example will switch off the device with the identifier '11657 0240192': ::

    $ fritzhomeauto -i 192.168.178.1 -p <password> -s '11657 0240192' off


Example on how to get informations about the known devices by using a module: ::

    from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation

    fha = FritzHomeAutomation(address='192.168.178.1', password=<password>)
    info = fha.device_informations())

'info' is a list of dictionaries describing the devices: ::

    [{'NewAIN': '11657 0240192',
      'NewDeviceId': 16,
      'NewDeviceName': 'FRITZ!DECT 210 #1',
       ...
      'NewHkrComfortVentilStatus': 'CLOSED',
       ...
      'NewMultimeterEnergy': 75,
      'NewMultimeterIsEnabled': 'ENABLED',
       ...
      'NewSwitchState': 'ON',
      'NewTemperatureCelsius': 265,
      'NewTemperatureIsEnabled': 'ENABLED',
      'NewTemperatureIsValid': 'VALID',
      'NewTemperatureOffset': 0}]

Depending on the device, different informations will get reported. Informations about a specific device can get obtained with the identifier *NewAIN*. The next example shows how to get the temperature in °C, taken the *NewAIN* from device_informations() call: ::

    ain = '11657 0240192'
    fha.get_device_information_by_identifier(ain)['NewTemperatureCelsius'] * 0.1


It is also easy to toggle a switch (like a FRITZ!DECT 200/210 device): ::

    fha.set_switch(ain, on=True)

This will turn the switch with the given identifier *on* or *off* depending whether the parameter 'on' is **True** or **False**. Usecases can be to set a switch depending on the temperature or daytime.


FritzHomeAutomation  API
........................

.. automodule:: fritzconnection.lib.fritzhomeauto
    :members:


FritzHosts
----------

Utility modul for FritzConnection to list the known hosts. For all known hosts the current ip, name, the MAC address and the active-state are reported. Usage from the command line: ::

    $ fritzhosts -i 192.168.178.1 -p <password>

    FritzConnection v1.0
    FritzHosts for FRITZ!Box 7590 at ip 192.168.178.1
    FRITZ!OS: 7.12:

    List of registered hosts:

      n: ip               name                         mac                 status

      1: 192.168.178.36   DE-20HAR90XXXXX              00:E1:8C:9B:DF:98   -
      2: 192.168.178.33   HUAWEI-P20-Pro-xxxxxxxxxx    B4:CD:27:37:78:E4   -
         ...
     20: 192.168.178.24   fritz.repeater               C6:25:06:83:64:C5   active
     21: 192.168.178.25   fritzbox4020                 C8:0E:14:B8:71:DD   active

Example how to use FritzHost in a module to get the same output: ::

    from fritzconnection.lib.fritzhosts import FritzHosts

    fh = FritzHosts(address='192.168.178.1', password='password')
    hosts = fh.get_hosts_info()
    for index, host in enumerate(hosts, start=1):
        status = 'active' if host['status'] else  '-'
        ip = host['ip'] if host['ip'] else '-'
        mac = host['mac'] if host['mac'] else '-'
        hn = host['name']
        print(f'{index:>3}: {ip:<16} {hn:<28} {mac:<17}   {status}')


FritzHosts API
..............

.. automodule:: fritzconnection.lib.fritzhosts
    :members:



FritzStatus
-----------

Reports informations about the link-status to the service provider. Usage from the command line: ::

    $ fritzstatus -i 192.168.178.1 -p password

    FritzConnection v1.0
    FritzStatus for FRITZ!Box 7590 at ip 192.168.178.1
    FRITZ!OS: 7.12:

        is linked           : True
        is connected        : True
        external ip (v4)    : 79.255.xxx.xxx
        external ip (v6)    : 2003:ee:xx:x:x
        uptime              : 190:30:56
        bytes send          : 2097630835
        bytes received      : 2866333236
        max. bit rate       : ('9.9 MBit/s', '50.5 MBit/s')

For periodic calls, an instance of FritzStatus (resp. FritzConnection) should only created once: ::

    import time
    from fritzconnection.lib.fritzstatus import FritzStatus

    fc = FritzStatus(address='192.168.178.1', password='password')
    while True:
        print(fc.str_transmission_rate)
        time.sleep(2)

This will report an output like this: ::

    ('992.0 bytes', '23.6 KB')
    ('0.0 bytes', '0.0 bytes')
    ('1.3 KB', '25.4 KB')
    ('3.7 KB', '36.4 KB')
    ('21.2 KB', '104.6 KB')


FritzStatus API
...............

.. automodule:: fritzconnection.lib.fritzstatus
    :members:

