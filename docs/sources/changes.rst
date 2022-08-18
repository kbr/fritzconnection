

Version History
===============


development
-----------

- FritzConnection

  - API cache integration added: for faster start up times the router API can optional get saved in a cache-file. This can save up to several seconds run-time on instanciation.

- FritzHosts:

  - New method `get_hosts_attributes` providing a list of dictionaries with the attribues of all known hosts (#134)

- FritzStatus:

  - New property `update_available` (#156)
  - New property `connection_service`
  - New property `has_wan_support` (#162)
  - New property `has_wan_enabled` (#147)
  - New property `device_has_mesh_support` (#146)
  - New method `get_default_connection_service` (#146)
  - New method `upnp_enabled()` (#153)

- FritzWLAN:

  - QR-code now supports encryption information for the described network by auto-detecting the security settings (which is optional but set to default) (#139)

- Testing:

  - requires opencv to check qr-codes
  - covering Python 3.11

- New class `ArgumentNamespace` added in `fritzconnection.core.utils` for convenient handling of dictionaries returned from  `FritzConnection.call_action()` calls.
- Better error message in case application access is disabled (#142)



1.9.1 - 2022-01-17
------------------

- bugfix: AttributeError in `FritzHomeAutomation.device_information()` removed - bug introduced in 1.9.0 (#138)
- enhancement: `FritzWLAN.get_wifi_qr_code()` forwards the optional `security` and `hidden` parameters to `segno`. (#139)


1.9.0 - 2022-01-05
------------------

- FritzWLAN:

  - New method `get_wifi_qr_code()` for QR-code creation for wifi-access (#133). Requires `segno` as dependency. See `installation <./install.html>`_ for  details. The method is also inherited by FritzGuestWLAN.
  - New method `channel_info()` (#131)

- FritzHomeAutomation: New method `device_information()` (#131)
- Deprecations:

  - `fritzconnection.lib.fritzhomeauto.FritzHomeAutomation.device_informations()`
  - `fritzconnection.lib.fritzstatus.FritzStatus.uptime()`
  - `fritzconnection.lib.fritzwlan.FritzWLAN.channel_infos()`

- Documentation improvements


1.8.0 - 2021-12-27
------------------

- FritzConnection: new command line option `-R` to reboot the system
- FritzHosts:

  - New method `get_generic_host_entries` returning a generator to iterate over all entries as reported by the method `get_generic_host_entry`.
  - The methods `get_active_hosts` and `get_hosts_info` provide additional host attributes (#127)

- Refactoring of the logging module `fritzconnection.core.logger` (introduced in 1.7.0). Now emitting messages from INFO-level and up by default.
- Connection errors with the router raised from the underlying `urllib3` library are caught and raised again as FritzConnectionException preserving the connection error information (#128)


1.7.2 - 2021-11-14
------------------

- bugfix: logger deactivated by default (#123)


1.7.1 - 2021-10-10
------------------

- Tests extended for Python 3.10


1.7.0 - 2021-09-25
------------------

- New FritzWLAN-methods:

  - `enable` and `disable` to enable and disable a wlan network.
  - `get_password` and `set_password` to get the current password or set a new one for a wlan network.

- New FritzGuestWLAN library class.
- New FritzConnection method `reboot`.
- New logging module `fritzconnection.core.logger`.


1.6.0 - 2021-07-24
------------------

- New arguments for FritzConnection: `pool_connections` and `pool_maxsize` to adapt the default urllib3 settings (used by requests). (#114).
- New properties `FritzStatus.device_uptime` and `FritzStatus.connection_uptime``; the latter a replacement for `FritzStatus.uptime` – still existing as an alias. (#104)
- bugfix: html-escape arguments in case that special characters are allowed by the protocol. (#115)
- bugfix: `FritzStatus.bytes_sent` will return the 32 bit value from older Fritz!Box models. (#110)
- bugfix: raise `FritzActionError` on accessing the mesh topology information from a device not having accesss to this information. (#107)
- adding code-of-conduct and contributing files to the repository.


1.5.0 - 2021-05-01
------------------

- Compatibility with Fritz!OS 7.24 and newer: takes the last logged in username as default in case that a username is not provided.


1.4.2 - 2021-03-06
------------------

- bugfix: byte_formatter may return wrong numbers on values < 1 and has raised math domain error on values == 0. (bug introduced with version 1.4.1) (#87)


1.4.1 - 2021-02-13
------------------

- bugfix: FritzStatus library now returns a 32 bit value for *bytes_received* for older Fritz!OS versions not providing the newer 64 bit information instead of raising an exception. (bug introduced with version 1.3.0) (#82)
- change: Output of bitrate changed to log10 based calculation (#45, #52)


1.4.0 - 2020-11-29
------------------

- New core module fritzmonitor for reporting realtime phone call events (#76).
- Library class FritzStatus with additional properties: *attenuation*, *str_attenuation*, *noise_margin* and *str_noise_margin* (#69)
- Library class FritzHost with additional method *get_host_name* (#75)
- Namespace prefix for xml-arguments removed (#66)
- Test extended for Python 3.9 (#73)


1.3.4 - 2020-08-06
------------------

- bugfix: session ignored timeout settings (#63)


1.3.3 - 2020-07-17
------------------

- bugfix: soap-xml encoding corrected (#59)
- bugfix: soap-xml tag-attribute separation fixed (#60)


1.3.2 - 2020-07-11
------------------

- bugfix: converting arguments returned from soap calls (#58)


1.3.1 - 2020-06-28
------------------

- authorisation now supports 'myfritz.net' access (#48)
- internal refactorings


1.3.0 - 2020-06-21
------------------

- Library class FritzStatus reports the sent and received bytes now as 64 bit integers and provides easy access to realtime monitor data.
- Library class FritzHost provides more methods to access devices, including *wake on LAN* and net topology information.
- Library class FritzPhonebook has a new method *get_all_name_numbers()* to fix a bug of *get_all_names()* reporting just one name in case that a phonebook holds multiple entries of the same name.
- Boolean arguments send to the router as *1* and *0* can also be given as the Python datatypes *True* and *False* (#30).
- Flag -c added to fritzconnection cli interface to report the complete api.
- pip installation no longer includes the tests (#39).
- pypi classifier changed to *Development Status :: 5 - Production/Stable*


0.8.5 - 2020-06-01
------------------

- updates the pinned lxml-dependency from version 4.3.4 to 4.5.1
- last version to support Python 2.7, <=3.5 (no more updates)


1.2.1 - 2020-03-21
------------------

- Library modules handling complex datatypes (urls) can now reuse fritzconnection sessions.


1.2.0 - 2020-01-07
------------------

- TLS for router communication added.
- Command line tools take the new option -e for encrypted connection.
- Sessions added for faster connections (significant speed up for TLS)
- Functional tests added addressing a physical router. Skipped if no router present.
- Bugfix for rendering the documentation of the FritzPhonebook-API (bug introduced in 1.1.1)


1.1.1 - 2019-12-29
------------------

- Bugfix in FritzConnection default parameters preventing the usage of library modules (bug introduced in 1.1.0)
- Minor bugfix in FritzPhonebook storing image-urls


1.1.0 - 2019-12-28
------------------

- FritzConnection takes a new optional parameter `timeout` limiting the time waiting for a router response.
- FritzPhonebook module rewritten for Python 3 without lxml-dependency and added again to the library (missing in version 1.0).
- Library module FritzStatus adapted to Python 3.

1.0.1 - 2019-12-21
------------------

- Bugfix in fritzinspection for command line based inspection of the Fritz!Box API.


1.0.0 - 2019-12-20
------------------

- Requires Python 3.6 or newer. The 0.8.x release is the last version supporting Python 2.7 and Python 3 up to 3.5
- The ``lxml`` library is no longer a dependency.
- New project layout. Library modules are now located in the new ``lib`` package.
- Rewrite of the description parser.
- Errors reported by the Fritz!Box are now raising specific exceptions.


0.8.4 - 2019-12-16
------------------

- Bugfix in connection.reconnect(). This bug has been introduced with version 0.8.0. For versions 0.8.0 to 0.8.3 'reconnect' requires a password because of a changed service call.
- Documentation updated.


0.8.3 - 2019-09-09
------------------

- Fix broken test (new in version 0.8.0)
- Minor code enhancements


0.8.2 - 2019-08-27
------------------

- Unified version numbering of the modules.
- ServiceError, ActionError and AuthorizationError are also importable from the package.
- Some code cleanup.

Changes in the development process: .hgignore removed and .gitignore added, changes in setup.py, readme changed to restructured text.

As Atlassian has announced to drop support for mercurial on ``bitbucket`` und will remove the according repositories (in June 2020), development of fritzconnection has converted from ``hg`` to ``git`` and the repository has been transfered to ``github``. Unfortunately the issue- and discussion-history will be lost this way (even by keeping the new git-repository at bitbucket).


0.8.1 - 2019-08-24
------------------

FritzStatus: bugfix requiring a password in combination with fritzconnection >= 0.8.0

FritzStatus: added the ``external_ipv6`` attribute

FritzStatus: added the ``max_linked_bit_rate`` attribute for the physical rate. Also added the ``str_max_linked_bit_rate`` attribute for a more readable output. (password must be provided for these infomations)

FritzConnection: added the ``AuthorizationError`` exception.


0.8.0 - 2019-08-20
------------------

Bugfix how servicenames are extracted from the xml-description files. However, the api has not changed.

The requirements are now fixed for lxml (4.3.4) and requests (2.22.0) as these versions are still supporting python 2.7


0.7.1 - 0.7.3 ~ 2019-07-24
--------------------------

Bugfixes, no new features or other changes.


0.7.0 - 2019-07-21
------------------

FritzConnection does now check for the environment variables ``FRITZ_USER`` and ``FRITZ_PASSWORD`` in case that neither user nor password are given.

FritzStatus now accepts user and password as keyword-parameters. Keep in mind, that FritzBoxes may return different information about the status depending whether these are gathered with or without a password.


0.6.5 - 2017-07-12
------------------

There is a new attribute *package_version*:

    >>> import fritzconnection
    >>> fritzconnection.package_version
    0.6.5

Because every module of the fritzconnection-package has it's own version, version-history of the package gets confusing over time. From now on every change of the content of the package is indicated by the the package-version. Every unchanged module keeps it's version. So i.e. the recent package-version is 0.6.5 but the fritzconnection-module is still in version 0.6 cause nothing has changed in this module since then.


0.6
---

FritzConnection now uses long qualified names as ``servicename``, i.e. ``WLANConfiguration:1`` or ``WLANConfiguration:2``. So these servicenames can now be used to call actions on different services with the same name:

    >>> connection = FritzConnection()
    >>> info = connection.call_action('WANIPConnection:2', 'GetInfo')

For backward compatibility servicename-extensions like ':2' can be omitted on calling 'call_action'. In this case FritzConnection will use the extension ':1' as default.

On calling unknown services or actions in both cases KeyErrors has been raised. Calling an unknown service (or one unaccessible without a password) will now raise a ``ServiceError``. Calling an invalid action on a service will raise an ``ActionError``. Both Exceptions are Subclasses from the new ``FritzConnectionException``. The Exception classes can get imported from fritzconnection:

    >>> from fritzconnection import ServiceError, ActionError


< 0.6
-----

Continuous update of features and bugfixes since first import at 2013-05-01 on bitbucket using mercurial.
