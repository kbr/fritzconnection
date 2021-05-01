Library Modules
===============

The library is a package with modules on top of FritzConnection to address specific tasks. The library-modules may not serve every need, but should be seen as examples on how to use FritzConnection and how to write more specialised modules.

**Performance considerations:**

Creating a FritzConnection instance will inspect the Fritz!Box API to get informations about all availabe services and corresponding actions. As this is i/o based it's generally slow. But once an instance is created, it can be reused for all tasks. Therefore the library classes can optionally initialised with an existing FritzConnection instance, to not inspect the router-API multiple times: ::

    from fritzconnection import FritzConnection
    from fritzconnection.lib.fritzhomeauto import FritzHomeAutomation
    from fritzconnection.lib.fritzwlan import FritzWLAN

    fc = FritzConnection(address='192.168.178.1', password=<password>)

    # library modules can be initialised with an existing FritzConnection instance
    fw = FritzWLAN(fc)
    print(fw.total_host_number)

    fh = FritzHomeAutomation(fc)  # same here: use existing instance for initialisation
    ain = '11657 0240192'  # assume the AIN of the switch is known
    fh.set_switch(ain, on=True)

The next sections will describe the library modules in detail.

**Inheritance from a common base class:**

All library modules inherit from a common abstract base class that should not get instantiated:

.. automodule:: fritzconnection.lib.fritzbase
    :members:


FritzCall
---------

Can dial phone numbers and allows access to history of phone calls: incoming, outgoing and missed ones. Usage from the command line: ::

    $ fritzcall -i 192.168.178.1 -p <password> -t in -d 7
    FRITZ!Box 7590 at ip 192.168.178.1
    FRITZ!OS: 7.12

    List of calls: in

      type   number                           date/time    duration

      ...
      more entries here
      ...


The flag ``-t`` indicates the type of calls to get listed: ``in | out | missed``. It ``-t`` is not given, all calls are listed (up to 999). The flag ``-d`` is the number of days to look back for calls e.g. 1: calls from today and yesterday, 7: calls from the complete last week.

FritzCall provides to dial numbers by the method ``dial``. This method can also invoked by the command line with the flag ``-c`` or ``--call``. *Note:* To make this work it is required to activate the dial-help service of the router first. ::

    $ fritzcall -i 192.168.178.1 -p <password> -c <phonenumber>
    dialing number: <phonenumber>
    dialing done, please wait for signal.


For using a module here is an example to list all missed calls: ::

    from fritzconnection.lib.fritzcall import FritzCall

    fc = FritzCall(address='192.168.178.1', password=<password>)
    calls = fc.get_missed_calls()
    for call in calls:
        print(call)

Calling back the last missed call is easy: ::

    missed_number = calls[0].Caller  # Caller attribute holds the number
    fc.dial(missed_number)  # now dial it

The module provides some constants that can be used with the get_calls() method as arguments for the calltype parameter: ::

    ALL_CALL_TYPES = 0
    RECEIVED_CALL_TYPE = 1
    MISSED_CALL_TYPE = 2
    OUT_CALL_TYPE = 3
    ACTIVE_RECEIVED_CALL_TYPE = 9
    REJECTED_CALL_TYPE = 10
    ACTIVE_OUT_CALL_TYPE = 11


FritzCall  API
..............

.. automodule:: fritzconnection.lib.fritzcall
    :members:




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
    info = fha.device_informations()

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

This will turn the switch with the given identifier *on* or *off* depending whether the parameter 'on' is *True* or *False*. Usecases can be to set a switch depending on the temperature or daytime.


FritzHomeAutomation  API
........................

.. automodule:: fritzconnection.lib.fritzhomeauto
    :members:


FritzHosts
----------

Utility modul for FritzConnection to access and control the known hosts. The command line tool allows to list the current ip, name, the MAC address and the active-state for all registered hosts: ::

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



FritzPhonebook
--------------

Allows read-only access to the phonebooks stored in the router (a Fritz!Box router can have more than a single phonebook). The command line interface allows inspection of the phonebooks and search for name and numbers. The flag ``-a`` will list the content of all phonebooks: ::

    $ fritzphonebook -i 192.168.178.1 -p <password> -a

    FritzConnection v1.1
    FritzPhonebook for FRITZ!Box 7590 at ip 192.168.178.1
    FRITZ!OS: 7.12

    Content of phonebook: business
    good customer                 0123456789
    another good customer         0987654321
    ...
    more numbers here
    ...

With the flags ``--name`` and ``--number`` like ``--name "good customer"`` and ``--number 0987654321`` all phonebooks will get searched for the according entry.

Here is an example to list the entries of all phonebooks by means of a module: ::

    from fritzconnection.lib.fritzphonebook import FritzPhonebook

    fp = FritzPhonebook(address='192.168.178.1', password='password')
    for phonebook_id in fp.phonebook_ids:
        contacts = fp.get_all_names(phonebook_id)
        for name, numbers in contacts.items():
            print(name, numbers)


FritzPhonebook API
..................

.. automodule:: fritzconnection.lib.fritzphonebook
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


FritzWLAN
---------

Module for accessing basic WLANConfiguration settings. The command line tool gives an overview of active devices: ::

    $ fritzwlan -i 192.168.178.1 -p <password>
    FRITZ!Box 7590 at ip 192.168.178.1
    FRITZ!OS: 7.12
    Hosts registered at WLANConfiguration1:
    WLAN name: the wlan name
    channel  : 6
    index  active                 mac                ip  signal   speed
        0       1   E2:25:06:83:64:C5    192.168.178.24      51      86

    Hosts registered at WLANConfiguration2:
    WLAN name: the wlan name
    channel  : 36
    index  active                 mac                ip  signal   speed
        0       1   A0:99:9B:10:09:81    192.168.178.28      91    1300


Example to get the total number of known WLAN-devices for all WLANConfigurations: ::

    from fritzconnection.lib.fritzwlan import FritzWLAN

    fw = FritzWLAN(address='192.168.178.1', password='password')
    print(fw.total_host_number)


Example: device tracking
........................

A common usecase for wlan-informations is device tracking. The following is a basic example how to do this. The example will poll the mac-addresses of all active devices. (For this a fixed tracking duration with a short poll-period is used. This may not be appropriate for real world programs.)
::

    import time
    import datetime
    import itertools

    from fritzconnection.lib.fritzwlan import FritzWLAN
    from fritzconnection.core.exceptions import FritzServiceError


    ADDRESS = '192.168.178.1'
    PASSWORD = 'the_password'  # should not be hardcoded for real usage

    # short time periods for demonstration purposes
    TRACKING_DURATION = 20
    TRACKING_PERIOD = 5


    def get_active_macs(fwlan):
        """
        Gets a FritzWLAN instance and returns a list of mac addresses
        from the active devices
        """
        active_macs = list()
        # iterate over all wlans:
        for n in itertools.count(1):
            fwlan.service = n
            try:
                hosts_info = fwlan.get_hosts_info()
            except FritzServiceError:
                break
            else:
                active_macs.extend(entry['mac'] for entry in hosts_info)
        return active_macs


    def report_devices(fwlan):
        active_macs = get_active_macs(fwlan)
        # decide here what to do with this information:
        # print the mac addresses
        for mac in active_macs:
            print(mac)
        print()  # empty line for readability


    def track_devices(tracking_duration, tracking_period):
        # instanciate FritzWLAN just once for reusage
        fwlan = FritzWLAN(address=ADDRESS, password=PASSWORD)
        stop = datetime.datetime.now() + tracking_duration
        while datetime.datetime.now() < stop:
            report_devices(fwlan)
            time.sleep(tracking_period)


    def main():
        tracking_duration = datetime.timedelta(seconds=TRACKING_DURATION)
        track_devices(tracking_duration, TRACKING_PERIOD)
        print('done.')


    if __name__ == '__main__':
        main()


FritzWLAN API
.............

.. automodule:: fritzconnection.lib.fritzwlan
    :members:

