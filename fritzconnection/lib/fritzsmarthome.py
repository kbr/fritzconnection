"""
Module to access home-automation devices by the FRITZ! Smart Home REST API (0.9.5)-Interface.


"""

from fritzconnection.core.fritzconnection import FritzConnection


SMARTHOME_PREFIX = "smarthome"
OVERVIEW_PREFIX = f"{SMARTHOME_PREFIX}/overview"


class FritzRESTApi:

    def __init__(self, fc=None, **kwargs):
        if fc is None:
            fc = FritzConnection(**kwargs)
        self.fc = fc
        self.last_status_code = None
        
    def _call_rest_api(self, method, path, uid, serial, payload):
        response = self.fc.call_rest_api(
            method, path, uid=uid, serial=serial, payload=payload
        )
        self.last_status_code = response.status_code
        return response.json()
    
    def _get(self, path, uid=None, serial=None, payload=None):
        return self._call_rest_api("get", path, uid, serial, payload)
        
    def _put(self, path, uid=None, serial=None, payload=None):
        return self._call_rest_api("put", path, uid, serial, payload)
        
    def _post(self, path, uid=None, serial=None, payload=None):
        return self._call_rest_api("post", path, uid, serial, payload)
        
    def _del(self, path, uid=None, serial=None, payload=None):
        return self._call_rest_api("del", path, uid, serial, payload)
        
    def get_overview(self) -> dict:
        """
        Returns a structured representation of all connected smart home entities.
        """
        return self._get(path=OVERVIEW_PREFIX)
        
    def get_devices(self) -> list[dict]:
        """
        Returns a list of dictionaries describing all physical devices.
        """
        return self._get(path=f"{OVERVIEW_PREFIX}/devices")
    
    def get_device(self, uid:str) -> dict:
        """
        Returns a description of the device with the given uid
        (which on FRITZ products is mostly the same as the ain).
        """
        return self._get(path=f"{OVERVIEW_PREFIX}/devices", uid=uid)
        
    def get_groups(self) -> list:
        """
        Returns a list of known groups.
        """
        return self._get(path=f"{OVERVIEW_PREFIX}/groups")
        
    def get_group(self, uid) -> dict:
        """
        Returns a description of the group with the given uid.
        """
        return self._get(path=f"{OVERVIEW_PREFIX}/groups", uid=uid)
        
    def get_units(self) -> list[dict]:
        """
        Returns a list of known units.
        """
        return self._get(path=f"{OVERVIEW_PREFIX}/units")
        
