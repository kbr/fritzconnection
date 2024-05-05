"""
fritzconnection

library to communicate with the AVM Fritz!Box
by the TR-064 protocoll and allowes access via the http-interface.
Provides also an interface for realtime call-monitoring.

for documentation refer:
https://avm.de/service/schnittstellen/
https://fritzconnection.readthedocs.io/
"""

__version__ = "1.13.2"

# import shortcuts
from .core.fritzconnection import FritzConnection
from .core.fritzmonitor import FritzMonitor
