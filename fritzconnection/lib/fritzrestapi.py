"""
Module to access home-automation devices by the FRITZ! Smart Home REST
API (0.9.5)-Interface.

This is mainly a wrapper for the low-level
`FritzConnection.call_rest_api()` method. The class FritzRESTApi
provides the get, put, post and delete methods as well a convenience
methods for the REST API endpoints.


"""

from fritzconnection.core.fritzconnection import FritzConnection


SMARTHOME_PREFIX = "smarthome"
OVERVIEW_PREFIX = f"{SMARTHOME_PREFIX}/overview"
OVERVIEW_DEVICES_PATH = f"{OVERVIEW_PREFIX}/devices"
OVERVIEW_GROUPS_PATH = f"{OVERVIEW_PREFIX}/groups"
OVERVIEW_UNITS_PATH = f"{OVERVIEW_PREFIX}/units"
OVERVIEW_TEMPLATES_PATH = f"{OVERVIEW_PREFIX}/templates"
OVERVIEW_TRIGGERS_PATH = f"{OVERVIEW_PREFIX}/triggers"
CONFIGURATION_PREFIX = f"{SMARTHOME_PREFIX}/configuration"
CONFIGURATION_DEVICES_PATH = f"{CONFIGURATION_PREFIX}/devices"
CONFIGURATION_UNITS_PATH = f"{CONFIGURATION_PREFIX}/units"
CONFIGURATION_GROUPS_PATH = f"{CONFIGURATION_PREFIX}/groups"
CONFIGURATION_TEMPLATES_PATH = f"{CONFIGURATION_PREFIX}/templates"
CONFIGURATION_CAPABILITIES_PATH = f"{CONFIGURATION_PREFIX}/templateCapabilities"
CONNECT_PREFIX = f"{SMARTHOME_PREFIX}/connect"
CONNECT_RADIOBASES_PATH = f"{CONNECT_PREFIX}/radioBases"
CONNECT_SUBSCRIPTIONSTATE_PATH = f"{CONNECT_PREFIX}/subscriptionState"
CONNECT_STARTSUBSCRIPTION_PATH = f"{CONNECT_PREFIX}/startSubscription"
CONNECT_STOPSUBSCRIPTION_PATH = f"{CONNECT_PREFIX}/stopSubscription"
CONNECT_RESETCODE_PATH = f"{CONNECT_PREFIX}/resetCode"
CONNECT_INSTALLCODE_PATH = f"{CONNECT_PREFIX}/installCode"


class FritzRESTApi:
    """
    Collection of convenience methods according to the FRITZ! Smart Home
    REST API (0.9.5)-Interface. The methods are representing the
    api-endpoints. The methods `get`, `put`, `post` and
    `delete` can also get called.
    An instance of FritzRESTApi must get created with a reference to a
    FritzConnection instance or must provide the keyword-arguments
    required to create a FritzConnection instance.
    """

    def __init__(self, fc=None, **kwargs):
        if fc is None:
            fc = FritzConnection(**kwargs)
        self.fc = fc
        self.last_status_code = None
        
    def _call_rest_api(self, method, path, uid, serial, payload, params=None):
        response = self.fc.call_rest_api(
            method, path, params=params, uid=uid, serial=serial, payload=payload
        )
        self.last_status_code = response.status_code
        return response.json()
    
    def get(self, 
            path: str, 
            uid: str|None = None, 
            serial: str|None = None, 
            payload: dict|None = None
        ) -> list[dict]|dict:
        """
        Makes a `get` request to the given endpoint. `uid` and `serial`
        a mutual exclusive. `payload` can hold additonal data to send to
        the unit.
        """
        return self._call_rest_api(
            method="get", 
            path=path, 
            uid=uid, 
            serial=serial, 
            payload=payload
        )
        
    def put(self, 
            path: str, 
            uid: str|None = None, 
            serial: str|None = None, 
            payload: dict|None = None
        ) -> list[dict]|dict:
        """
        Makes a `put` request to the given endpoint. `uid` and `serial`
        a mutual exclusive. `payload` can hold additonal data to send to
        the unit.
        """
        return self._call_rest_api(
            method="put", 
            path=path, 
            uid=uid, 
            serial=serial, 
            payload=payload
        )
        
    def post(self, 
            path: str, 
            uid: str|None = None, 
            serial: str|None = None, 
            params: dict|list[tuple]|bytes|None = None,
            payload: dict|None = None
        ) -> list[dict]|dict:
        """
        Makes a `post` request to the given endpoint. `uid` and `serial`
        a mutual exclusive. `payload` can hold additonal data to send to
        the unit. `params` is a dictionary, list of tuples or bytes to
        send in the query string for the Request.
        """
        return self._call_rest_api(
            method="post", 
            path=path, 
            uid=uid, 
            serial=serial, 
            payload=payload, 
            params=params
        )
        
    def delete(self, 
            path: str, 
            uid: str|None = None, 
            serial: str|None = None, 
            payload: dict|None = None
        ) -> list[dict]|dict:
        """
        Makes a `del` request to the given endpoint. `uid` and `serial`
        a mutual exclusive. `payload` can hold additonal data to send to
        the unit.
        """
        return self._call_rest_api(
            method="del", 
            path=path, 
            uid=uid, 
            serial=serial, 
            payload=payload
        )
        
    def get_overview(self) -> dict:
        """
        Returns a structured representation of all connected smart home
        entities.
        """
        return self.get(path=OVERVIEW_PREFIX)
        
    def get_devices(self) -> list[dict]:
        """
        Returns a list of dictionaries describing all physical devices.
        """
        return self.get(path=OVERVIEW_DEVICES_PATH)
    
    def get_device(self, uid: str) -> dict:
        """
        Returns a description of the device with the given `uid`
        (which on FRITZ products is mostly the same as the ain).
        """
        return self.get(path=OVERVIEW_DEVICES_PATH, uid=uid)
        
    def get_groups(self) -> list:
        """
        Returns a list of known groups.
        """
        return self.get(path=OVERVIEW_GROUPS_PATH)
        
    def get_group(self, uid: str) -> dict:
        """
        Returns a description of the group with the given `uid`.
        """
        return self.get(path=OVERVIEW_GROUPS_PATH, uid=uid)
        
    def get_units(self) -> list[dict]:
        """
        Returns a list of known units.
        """
        return self.get(path=OVERVIEW_UNITS_PATH)
        
    def get_unit(self, uid: str) -> dict:
        """
        Returns a description of the unit with the given `uid`.
        """
        return self.get(path=OVERVIEW_UNITS_PATH, uid=uid)
        
    def control_interfaces(self, uid: str, payload: dict|None = None) -> dict:
        """
        Updates the state of an existing unit given by `uid`. The
        `payload` hold the interface data according to
        `IF_putUnitInterfaces`. Returns a dict representing an empty
        response-body on success or a dict with an error description.
        """
        return self.put(path=OVERVIEW_UNITS_PATH, uid=uid, payload=payload)
        
    def get_templates(self) -> list[dict]:
        """
        Returns a list of template descriptions.
        """
        return self.get(path=OVERVIEW_TEMPLATES_PATH)
        
    def get_template(self, uid: str) -> dict:
        """
        Returns a template with the given `uid`.
        """
        return self.get(path=OVERVIEW_UNITS_PATH, uid=uid)
        
    def apply_template(self, uid: str, payload: dict|None = None) -> dict:
        """
        Take the `uid` of a template that should be applied. The
        `payload` holds the triggerEvent boolean. Returns an empty dict
        representing an empty reponse-body on success.
        """    

    def get_triggers(self) -> list[dict]:
        """
        Returns a list of trigger descriptions.
        """
        return self.get(path=OVERVIEW_TRIGGERS_PATH)
    
    def get_trigger(self, uid: str) -> dict:
        """
        Returns a trigger-description with the given `uid`.
        """
        return self.get(path=OVERVIEW_TRIGGERS_PATH, uid=uid)
        
    def set_trigger(self, uid: str, payload: dict|None = None) -> dict:
        """
        Enables or disables a trigger with the given uid. Returns an
        empty dict on success or a dict with an error message.
        """
        return self.put(path=OVERVIEW_TRIGGERS_PATH, uid=uid, payload=payload)
        
    def get_globals(self) -> dict:
        """
        Returns the state of smart home avmPresets for lamps and
        location.
        """
        return self.get(path=f"{OVERVIEW_PREFIX}/globals") 

    def get_device_configuration(self, uid: str) -> dict:
        """
        Returns a dict with the configuration of the device with the
        given `uid`.
        """
        return self.get(path=CONFIGURATION_DEVICES_PATH, uid=uid)
        
    def configure_device(self, uid: str, payload: dict|None = None) -> dict:
        """
        Configure and/or controls the device with the given `uid`. The
        `payload` hold device-specific information. Returns an empty dict
        on success and a dict with an error message otherwise.
        """
        return self.put(path=CONFIGURATION_DEVICES_PATH, uid=uid, payload=payload)
        
    def delete_device(self, uid: str) -> dict:
        """
        Deletes the given device from smart home control. Returns an
        empty dict on success or a dict with an error message.
        """
        return self.delete(path=CONFIGURATION_DEVICES_PATH, uid=uid)
        
    def get_unit_configuration(self, uid: str) -> dict:
        """
        Returns a dict with the configuration of the unit with the given
        `uid`. This differs from `get_device_configuration()` as a
        device can have multiple units.
        """
        return self.get(path=CONFIGURATION_UNITS_PATH, uid=uid)
    
    def configure_unit(self, uid: str, payload: dict|None = None) -> dict:
        """
        Configure and/or controls the unit with the given `uid`. The
        `payload` hold device-specific information. Returns an empty
        dict on success or a dict with an error message otherwise.
        """
        return self.put(path=CONFIGURATION_UNITS_PATH, uid=uid, payload=payload)
    
    def create_new_group(self, name: str, payload: dict|None = None) -> dict:
        """
        Creates a new group with the given `name` and members provided
        by the payload. Returns a dict with the UID of the new group on
        success or a dict with an error message.
        """
        return self.post(
            path=CONFIGURATION_GROUPS_PATH, 
            params=name, 
            payload=payload
        )
        
    def get_group_configuration(self, uid: str) -> dict:
        """
        Returns a dict describing the group with the given `uid` on
        success or a dict with an error message. 
        """
        return self.get(path=CONFIGURATION_GROUPS_PATH, uid=uid)
    
    def configure_group(self, uid: str, payload: dict|None = None) -> dict:
        """
        Configure and/or controls the group with the given `uid`. The
        `payload` hold device-specific information. Returns an empty
        dict on success or a dict with an error message otherwise.
        """
        return self.put(path=CONFIGURATION_GROUPS_PATH, uid=uid, payload=payload)
        
    def delete_group(self, uid: str) -> dict:
        """
        Deletes the group with the given `uid`. Returns an empty dict on
        success or a dict with an error message.
        """
        return self.delete(path=CONFIGURATION_GROUPS_PATH, uid=uid)
        
    def create_new_template(self, name: str, payload: dict|None = None) -> dict:
        """
        Creates a new template with the given `name` and members provided
        by the payload. Returns a dict with the UID of the new template on
        success or a dict with an error message.
        """
        return self.post(
            path=CONFIGURATION_TEMPLATES_PATH, 
            params=name, 
            payload=payload
        )
        
    def get_template_configuration(self, uid: str) -> dict:
        """
        Returns a dict describing the templste with the given `uid` on
        success or a dict with an error message. 
        """
        return self.get(path=CONFIGURATION_TEMPLATES_PATH, uid=uid)
    
    def configure_template(self, uid: str, payload: dict|None = None) -> dict:
        """
        Configure and/or controls the template with the given `uid`. The
        `payload` hold device-specific information. Returns an empty
        dict on success or a dict with an error message otherwise.
        """
        return self.put(path=CONFIGURATION_TEMPLATES_PATH, uid=uid, payload=payload)
        
    def delete_template(self, uid: str) -> dict:
        """
        Deletes the group with the given `uid`. Returns an empty dict on
        success or a dict with an error message.
        """
        return self.delete(path=CONFIGURATION_TEMPLATES_PATH, uid=uid)
   
    def get_template_configuration_capabilities(self) -> dict:
        """
        Return a dict with the template capabilities on success or a
        dict with an error message.
        """
        return self.get(path=CONFIGURATION_CAPABILITIES_PATH)
        
    def get_radio_bases(self) -> list[dict]|dict:
        """
        Returns a list of dicts describing available radio-bases on success or a
        dict with an error message.
        """
        return self.get(path=CONNECT_RADIOBASES_PATH)
    
    def get_radio_base(self, serial: str) -> dict:
        """
        Returns a dict with the descrition of the radio-base with the
        given `serial` on success or a dict with an error message.
        """
        return self.get(path=CONNECT_RADIOBASES_PATH, serial=serial)
    
    def get_subscription_state(self, uid: str) -> dict:
        """
        Returns a dict with the description of the subscription with the
        given uid on success or a dict with an error message.
        """
        return self.get(path=CONNECT_SUBSCRIPTIONSTATE_PATH, uid=uid)
        
    def start_subscription_on_radio_base(
        self, 
        serial: str, 
        payload: dict|None = None
    ) -> dict:
        """
        Starts a subscription on the radio-base given by serial with the
        configuration given by payload. Returns a dict with the new
        subscription UID on success or a dict with an error message.
        """
        return self.post(
            path=CONNECT_STARTSUBSCRIPTION_PATH, 
            serial=serial, 
            payload=payload
        )

    def stop_subscription_on_radio_base(self, serial: str) -> dict:
        """
        Stops a subscription on the radio-base with the given serial.
        Returns an empty dict on success or a dict with an error
        message.
        """
        return self.post(path=CONNECT_STOPSUBSCRIPTION_PATH, serial=serial)
        
    def set_resetcode_on_zigbee_radio_base(self, serial: str, reset_code: str) -> dict:
        """
        Send a Zigbee specific `reset_code` to the Zigbee device with
        the given `serial` for unpairing devices. Returns an empty dict
        on success or a dict with an error message.
        """
        payload = {"resetCode": reset_code}
        return self.post(path=CONNECT_RESETCODE_PATH, serial=serial, payload=payload)
        
    def set_installcode_on_zigbee_radio_base(
        self, 
        serial: str, 
        install_code: str, 
        device_address: str
    ) -> dict:
        """
        Takes the serial, the install_code and the device_address of a
        Zigbee device for secure pairing.  Returns an empty dict on
        success or a dict with an error message.
        """
        payload = {
            "installCode": install_code,
            "deviceAddress": device_address
        }
        return self.post(path=CONNECT_INSTALLCODE_PATH, serial=serial, payload=payload)

    # Example method how to use instances of FritzRESTApi (here the instance
    # is given as self). Every unit providing an onOffInterface can be set to
    # a new state. As there are many more devices like blinds, heat regulations
    # and so on (and even more may get added in the future), it makes no sense
    # to include all possible interfaces in this class. Instead classes
    # representing devices can get build on top of FritzRESTApi. So this
    # method serves mainly an an implementation template.
    def set_on_off_interface(self, uid:str, new_state:bool) -> dict:
        """
        Takes the `uid` of a unit providing an onOffInterface (like
        switches). The argument `new_state` will set the interface on a
        device able to switch something to on (True) or off (False).
        Returns an empty dict on success or a dict with an error
        message.
        
        Note::
           
           This method is mainly an implementation example for users
           reading the sources and want to know how to build the payload
           for units.
           
        """
        payload = {
            "interfaces": {
                "onOffInterface": {
                    'active': new_state
                }
            }
        }
        return self.control_interfaces(uid=uid, payload=payload)
