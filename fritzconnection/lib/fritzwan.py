"""
Access to the WAN information and settings of the router.
"""

from fritzconnection.core.fritzconnection import FritzConnection


class FritzWAN:
    """
    Common attributes and methods for all FritzBox routers with
    integrated WAN capabilities, regardless of the connection type (dsl,
    cable, fibre, lte).

    `fc`: instance of FritzConnection
    `service_prefix, connection_service, service_postfix` are the layer3
     information parts of the default connection service (as strings).
    """

    def __init__(self,
        fc: FritzConnection,
        service_prefix: str,
        connection_service: str,
        service_postfix: str,
        *args, **kwargs
    ):
        self.fc = fc
        self.service_prefix = service_prefix
        self.connection_service = connection_service
        self.service_postfix = service_postfix
        self.connection_service_name = connection_service + service_postfix
        self.args = args
        self.kwargs = kwargs

    @property
    def modelname(self) -> str:
        """
        The device modelname.
        Keep this property for backward compatibility.
        """
        return self.fc.device_name

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
    def str_max_linked_bit_rate(self) -> tuple[str, str]:
        """
        Human-readable maximum of the physical upstream- and
        downstream-rate in bits/sec. Value is a tuple, first item is
        upstream, second item is downstream.
        """
        upstream, downstream = self.max_linked_bit_rate
        return (
            format_rate(upstream, unit="bits"),
            format_rate(downstream, unit="bits"),
        )

    def get_common_link_properties(self) -> dict:
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

         """
        return self.fc.call_action(
            "WANCommonInterfaceConfig1", "GetCommonLinkProperties"
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


class FritzStatus:
    """
    Class returning an instance of a matching status class for the
    router connection type.
    """

    def __new__(cls, fc=None, *args, **kwargs):
        # Adapting the class to the router connection-type would normalwise
        # be a usecase for a metaclass or class-decorator.
        # But in this case the information about the connection-type is provided
        # by the router at runtime.
        if fc is None:
            fc = FritzConnection(*args, **kwargs)
        # this will raise a FritzServiceError if the device is not a WAN-device:
        result = fc.call_action("Layer3Forwarding1", "GetDefaultConnectionService")
        service_prefix, connection_service, service_postfix =\
            result["NewDefaultConnectionService"].split(".")
        if connection_service == "WANPPPConnection":
            # dsl-connection:
            bases = (DSLCableCommonMixin, FritzWAN)
        elif connection_service == "WANIPConnection":
            # cable-connection:
            bases = (DSLCableCommonMixin, FritzWAN)
        else:
            bases = (FritzWAN,)
        return type(cls.__name__, bases, {})(
            fc, service_prefix, connection_service, service_postfix, *args, **kwargs
        )
