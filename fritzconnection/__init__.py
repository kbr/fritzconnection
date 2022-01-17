"""
fritzconnection

library to communicate with the AVM Fritz!Box
via Soap and TR-064.
provides also interface for realtime call-monitoring.

for documentation refer:
https://avm.de/service/schnittstellen/
https://fritzconnection.readthedocs.io/
"""

__version__ = "1.9.1"

# import shortcuts
from .core.fritzconnection import FritzConnection
from .core.fritzmonitor import FritzMonitor
