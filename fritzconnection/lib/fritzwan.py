"""
Access to the WAN information and settings of the router.
"""

from fritzconnection.core.fritzconnection import FritzConnection


class BaseWAN:
    """
    Common attributes and methods for all FritzBox routers with
    integrated WAN capabilities, regardless of the connection type (dsl,
    cable, fibre, lte).
    """
    # Note: 
    # - the service WANIPConn1 is an alias for igd.WANIPConnection:1
    # - the service WANCommonIFC1 is an alias for igd.WANCommonInterfaceConfig:1
    # to prevent a name clash with the corresponding tr064 services.
            
    def __init__(self, fc, prefix, service, postfix):
        self.fc = fc
        self.prefix = prefix
        self.service = service
        self.postfix = postfix
        self.connection_service_name = f"{service}{postfix}"

    @property
    def is_linked(self) -> bool:
        """
        Returns a boolean whether the router has a physical WAN connection.
        """
        state = self.get_common_link_properties()["NewPhysicalLinkStatus"]
        return state.lower() == "up"

    @property
    def max_linked_bit_rate(self) -> tuple[int, int]:
        """
        Tuple with the maximum upstream- and downstream-rate
        of the physical link. The rate is given in bits/sec.
        """
        info = self.get_common_link_properties()
        return (
            info["NewLayer1UpstreamMaxBitRate"],
            info["NewLayer1DownstreamMaxBitRate"]
        )
    
    @property
    def external_ip(self):
        """
        Returns the external ipv4 address.
        This call is faster than via `get_status_information`.
        """
        result = self.fc.call_action("WANIPConn", "GetExternalIPAddress")
        return result["NewExternalIPAddress"]
        
    @property
    def external_ipv6(self) -> str:
        """The external v6 ip-address."""
        return self.external_ipv6_info["NewExternalIPv6Address"]

    @property
    def external_ipv6_info(self) -> dict:
        """
        Returns the ipv6 external address information as a dictionary with the keys:
        NewExternalIPv6Address                   out ->     string
        NewPrefixLength                          out ->     ui1
        NewValidLifetime                         out ->     ui4
        NewPreferedLifetime                      out ->     ui4
        """
        return self.fc.call_action("WANIPConn", "X_AVM_DE_GetExternalIPv6Address")

    @property
    def ipv6_prefix(self):
        """The internal v6 prefix."""
        return self.ipv6_prefix_info["NewIPv6Prefix"]

    @property
    def ipv6_prefix_info(self) -> dict:
        """
        Returns the ipv6 prefix information as a dictionary with the keys:
        NewIPv6Prefix                            out ->     string
        NewPrefixLength                          out ->     ui1
        NewValidLifetime                         out ->     ui4
        NewPreferedLifetime                      out ->     ui4
        """
        return self.fc.call_action("WANIPConn", "X_AVM_DE_GetIPv6Prefix")

    @property
    def connection_uptime(self) -> int:
        """Connection uptime in seconds."""
        status = self.fc.call_action("WANIPConn", "GetStatusInfo")
        return status["NewUptime"]
        
    def get_addon_info(self) -> dict:
        """
        Returns a dictionary with the following information:
        
            'NewByteSendRate'
            'NewByteReceiveRate'
            'NewPacketSendRate'
            'NewPacketReceiveRate'
            'NewTotalBytesSent'
            'NewTotalBytesReceived'
            'NewAutoDisconnectTime'
            'NewIdleDisconnectTime'
            'NewDNSServer1'
            'NewDNSServer2'
            'NewVoipDNSServer1'
            'NewVoipDNSServer2'
            'NewUpnpControlEnabled'
            'NewRoutedBridgedModeBoth'
            'NewX_AVM_DE_TotalBytesSent64'
            'NewX_AVM_DE_TotalBytesReceived64'
            'NewX_AVM_DE_WANAccessType'
            'NewX_AVM_DE_Layer1UpstreamMaxBitRate64'
            'NewX_AVM_DE_Layer1DownstreamMaxBitRate64'
        """
        return self.fc.call_action("WANCommonIFC1", "GetAddonInfos")

    def get_common_link_properties(self) -> dict:
        """
        Returns a dictionary with the following information:

            'NewWANAccessType'
            'NewLayer1UpstreamMaxBitRate'
            'NewLayer1DownstreamMaxBitRate'
            'NewPhysicalLinkStatus'
            
        This method utilizes the igd.WANCommonInterfaceConfig service.
        The bit rates are the synchronized rates between the router and
        provider.
        """
        return self.fc.call_action(
            "WANCommonIFC1", "GetCommonLinkProperties"
        )
        
    def get_avm_common_link_properties(self) -> dict:
        """
        Returns a dictionary with the following information:
        
            'NewWANAccessType'
            'NewLayer1UpstreamMaxBitRate'
            'NewLayer1DownstreamMaxBitRate'
            'NewPhysicalLinkStatus'
            'NewX_AVM-DE_DownstreamCurrentUtilization'
            'NewX_AVM-DE_UpstreamCurrentUtilization'
            'NewX_AVM-DE_DownstreamCurrentMaxSpeed'
            'NewX_AVM-DE_UpstreamCurrentMaxSpeed'        

        This method utilizes the tr064.WANCommonInterfaceConfig service.
        The bit rates are the physical possible rates between the router
        and provider.
        """
        return self.fc.call_action(
            "WANCommonInterfaceConfig", "GetCommonLinkProperties"
        )

    def get_application_remote_info(self) -> dict:
        """
        Returns a dictionary with the following information:

            'NewSubnetMask'
            'NewIPAddress'
            'NewExternalIPAddress'
            'NewExternalIPv6Address'
            'NewRemoteAccessDDNSEnabled'
            'NewRemoteAccessDDNSDomain'
            'NewMyFritzEnabled'
            'NewMyFritzDynDNSName'

        """
        return self.fc.call_action("X_AVM-DE_AppSetup1", "GetAppRemoteInfo")

    def get_status_information(self) -> dict:
        """
        Returns a dictionary with collected data for a device status representation.
        """
        def bit_to_megabit(bit):
            return f"{round(bit / 1e6, 2)} MBit/sec"

        info = self.get_common_link_properties()
        info.update(self.get_application_remote_info())
        status_information = {
            "connection type": info["NewWANAccessType"],
            "is physical linked": info["NewPhysicalLinkStatus"],
            "downstream_max_bitrate": info["NewLayer1DownstreamMaxBitRate"],
            "upstream_max_bitrate": info["NewLayer1UpstreamMaxBitRate"],
            "max. downstream": bit_to_megabit(info["NewLayer1DownstreamMaxBitRate"]),
            "max. upstream": bit_to_megabit(info["NewLayer1UpstreamMaxBitRate"]),
        }
        external_ip = info["NewExternalIPAddress"]
        external_ipv6 = info["NewExternalIPv6Address"]
        if external_ip:
            status_information["external ip"] = external_ip
        if external_ipv6 and external_ipv6 != external_ip:
            status_information["external ipv6"] = external_ipv6
        return status_information

    @staticmethod
    def format_uptime(seconds: str|int) -> str:
        """
        Takes seconds as integer and returns a string like
        '1 days, 2 hours, 3 minutes, 4 seconds'
        """
        seconds = int(seconds)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        days, hours = divmod(hours, 24)
        return ", ".join(
            f"{value} {unit}" for value, unit in zip(
                (days, hours, minutes, seconds),
                ("days", "hours", "minutes", "seconds")
            ) if value
        )


class DSLCableCommonMixin:
    """
    Common service/actions for cable and dsl connections. Service names
    are connection-specific, but the action names are identic as well as
    the return values.
    """
    
    @property
    def is_connected(self) -> bool:
        """
        True if wan is enabled otherwise False.
        This is not the same as is_linked, which is the physical link.
        """
        info = self.fc.call_action(self.connection_service_name, "GetInfo")
        return info["NewEnable"]
        
    @property
    def connection_uptime(self) -> int:
        """
        Returns the connection uptime in seconds.
        """
        info = self.fc.call_action(self.connection_service_name, "GetStatusInfo")
        try:
            uptime = int(info["NewUptime"])
        except ValueError:
            # no uptime available
            uptime = 0
        return uptime

    def force_termination(self):
        """
        Reconnect the current connection with a (maybe) new ip.
        """
        self.fc.call_action(self.connection_service_name, "ForceTermination")

    def get_status_information(self):
        """
        Gather status information for a PPP or IP connection
        """
        status_information = super().get_status_information()
        info = self.fc.call_action(self.connection_service_name, "GetStatusInfo")
        status_information["connection status"] = info["NewConnectionStatus"]
        status_information["uptime"] = self.format_uptime(info["NewUptime"])
        return status_information


class DSLConnection:

    def __str__(self):
        return f"WAN: DSL connection\n{self.fc}"
        
    @property
    def noise_margin(self) -> tuple[int, int]:
        """
        Tuple of noise margin. First item
        is upstream, second item downstream.
        """
        status = self.fc.call_action("WANDSLInterfaceConfig1", "GetInfo")
        upstream = status["NewUpstreamNoiseMargin"]
        downstream = status["NewDownstreamNoiseMargin"]
        return upstream, downstream

    @property
    def attenuation(self) -> tuple[int, int]:
        """
        Tuple of attenuation. First item
        is upstream, second item downstream.
        """
        status = self.fc.call_action("WANDSLInterfaceConfig1", "GetInfo")
        upstream = status["NewUpstreamAttenuation"]
        downstream = status["NewDownstreamAttenuation"]
        return upstream, downstream


class CableConnection:

    def __str__(self):
        return f"WAN: Cable connection\n{self.fc}"
        

class FritzWAN:
    """
    Class returning an instance matching the router connection type.
    """

    def __new__(cls, fc=None, **kwargs):
        # Adapting the class to the router connection-type would normalwise
        # be a usecase for a metaclass or class-decorator.
        # But in this case the information about the connection-type is provided
        # by the router at runtime.
        if fc is None:
            fc = FritzConnection(**kwargs)
        # this will raise a FritzServiceError if the device is not a WAN-device:
        result = fc.call_action("Layer3Forwarding1", "GetDefaultConnectionService")
        prefix, service, postfix = result["NewDefaultConnectionService"].split(".")
        bases = {
            "WANPPPConnection": (DSLConnection, DSLCableCommonMixin, BaseWAN),
            "WANIPConnection": (CableConnection, DSLCableCommonMixin, BaseWAN),
        }.get(service, (BaseWAN,))
        return type(cls.__name__, bases, {})(fc, prefix, service, postfix)
