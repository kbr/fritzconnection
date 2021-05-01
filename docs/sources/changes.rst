

Version History
===============

1.5.0
-----

- Compatibility with Fritz!OS 7.24 and newer: takes the last logged in username as default in case that a username is not provided.


1.4.2
-----

- bugfix: byte_formatter may return wrong numbers on values < 1 and has raised math domain error on values == 0. (bug introduced with version 1.4.1) (#87)


1.4.1
-----

- bugfix: FritzStatus library now returns a 32 bit value for *bytes_received* for older Fritz!OS versions not providing the newer 64 bit information instead of raising an exception. (bug introduced with version 1.3.0) (#82)
- change: Output of bitrate changed to log10 based calculation (#45, #52)


1.4.0
-----

- New core module fritzmonitor for reporting realtime phone call events (#76).
- Library class FritzStatus with additional properties: *attenuation*, *str_attenuation*, *noise_margin* and *str_noise_margin* (#69)
- Library class FritzHost with additional method *get_host_name* (#75)
- Namespace prefix for xml-arguments removed (#66)
- Test extended for Python 3.9 (#73)


1.3.4
-----

- bugfix: session ignored timeout settings (#63)


1.3.3
-----

- bugfix: soap-xml encoding corrected (#59)
- bugfix: soap-xml tag-attribute separation fixed (#60)


1.3.2
-----

- bugfix: converting arguments returned from soap calls (#58)


1.3.1
-----

- authorisation now supports 'myfritz.net' access (#48)
- internal refactorings


1.3.0
-----

- Library class FritzStatus reports the sent and received bytes now as 64 bit integers and provides easy access to realtime monitor data.
- Library class FritzHost provides more methods to access devices, including *wake on LAN* and net topology informations.
- Library class FritzPhonebook has a new method *get_all_name_numbers()* to fix a bug of *get_all_names()* reporting just one name in case that a phonebook holds multiple entries of the same name.
- Boolean arguments send to the router as *1* and *0* can also be given as the Python datatypes *True* and *False* (#30).
- Flag -c added to fritzconnection cli interface to report the complete api.
- pip installation no longer includes the tests (#39).
- pypi classifier changed to *Development Status :: 5 - Production/Stable*


1.2.1
-----

- Library modules handling complex datatypes (urls) can now reuse fritzconnection sessions.


1.2.0
-----

- TLS for router communication added.
- Command line tools take the new option -e for encrypted connection.
- Sessions added for faster connections (significant speed up for TLS)
- Functional tests added addressing a physical router. Skipped if no router present.
- Bugfix for rendering the documentation of the FritzPhonebook-API (bug introduced in 1.1.1)


1.1.1
-----

- Bugfix in FritzConnection default parameters preventing the usage of library modules (bug introduced in 1.1)
- Minor bugfix in FritzPhonebook storing image-urls


1.1
---

- FritzConnection takes a new optional parameter `timeout` limiting the time waiting for a router response.
- FritzPhonebook module rewritten for Python 3 without lxml-dependency and added again to the library (missing in version 1.0).
- Library module FritzStatus adapted to Python 3.

1.0.1
-----

- Bugfix in fritzinspection for command line based inspection of the Fritz!Box API.


1.0
---

- Requires Python 3.6 or newer. The 0.8.x release is the last version supporting Python 2.7 and Python 3 up to 3.5
- The ``lxml`` library is no longer a dependency.
- New project layout. Library modules are now located in the new ``lib`` package.
- Rewrite of the description parser.
- Errors reported by the Fritz!Box are now raising specific exceptions.


0.8.5
-----

- updates the pinned lxml-dependency from version 4.3.4 to 4.5.1


0.8.4
-----

- Bugfix in connection.reconnect(). This bug has been introduced with version 0.8.0. For versions 0.8.0 to 0.8.3 'reconnect' requires a password because of a changed service call.
- Documentation updated.


0.8.3
-----

- Fix broken test (new in version 0.8.0)
- Minor code enhancements


0.8.2
-----

- Unified version numbering of the modules.
- ServiceError, ActionError and AuthorizationError are also importable from the package.
- Some code cleanup.

Changes in the development process: .hgignore removed and .gitignore added, changes in setup.py, readme changed to restructured text.

As Atlassian has announced to drop support for mercurial on ``bitbucket`` und will remove the according repositories (in June 2020), development of fritzconnection has converted from ``hg`` to ``git`` and the repository has been transfered to ``github``. Unfortunately the issue- and discussion-history will be lost this way (even by keeping the new git-repository at bitbucket).


0.8.1
-----

FritzStatus: bugfix requiring a password in combination with fritzconnection >= 0.8.0

FritzStatus: added the ``external_ipv6`` attribute

FritzStatus: added the ``max_linked_bit_rate`` attribute for the physical rate. Also added the ``str_max_linked_bit_rate`` attribute for a more readable output. (password must be provided for these infomations)

FritzConnection: added the ``AuthorizationError`` exception.


0.8.0
-----

Bugfix how servicenames are extracted from the xml-description files. However, the api has not changed.

The requirements are now fixed for lxml (4.3.4) and requests (2.22.0) as these versions are still supporting python 2.7


0.7.1 - 0.7.3
-------------

Bugfixes, no new features or other changes.


0.7.0
-----

FritzConnection does now check for the environment variables ``FRITZ_USER`` and ``FRITZ_PASSWORD`` in case that neither user nor password are given.

FritzStatus now accepts user and password as keyword-parameters. Keep in mind, that FritzBoxes may return different informations about the status depending whether these are gathered with or without a password.


0.6.5
-----

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



