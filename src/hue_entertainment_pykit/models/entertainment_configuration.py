"""
This module provides classes and enums for representing and managing the configuration of Philips Hue Entertainment
areas. It includes classes for defining resource types, configuration types, status types, and various components
used in the setup of Entertainment areas, such as channels, proxy nodes, and service locations.

Classes and Enums:
- ResourceTypes: Enum for different types of resources in the Philips Hue system.
- ConfigurationTypes: Enum for different types of configurations for Philips Hue Entertainment areas.
- StatusTypes: Enum for status types of Philips Hue Entertainment areas.
- ProxyMode: Enum for the proxy modes available in the Philips Hue system.
- Position: Dataclass representing a 3D coordinate position.
- ResourceIdentifier: Dataclass for identifying specific resources in the Philips Hue system.
- SegmentReference: Dataclass representing a reference to a segment of a resource.
- EntertainmentChannel: Dataclass representing a channel within a Philips Hue Entertainment area.
- StreamProxyNode: Dataclass representing a node in a stream proxy configuration.
- StreamProxy: Dataclass representing the stream proxy configuration.
- ServiceLocation: Dataclass representing the location of a service in a Philips Hue Entertainment area.
- Locations: Dataclass representing the locations of services in a Philips Hue Entertainment area.
- EntertainmentConfiguration: Class representing the configuration of a Philips Hue Entertainment area.

These classes and enums collectively enable the detailed and flexible representation of Entertainment area
configurations, facilitating the management and customization of lighting setups for entertainment purposes.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional, Any


class ResourceTypes(Enum):
    """
    Enumeration for different types of resources in the Philips Hue system.

    Each enum value represents a type of resource, such as entertainment areas and lights.
    """

    ENTERTAINMENT = "entertainment"
    LIGHT = "light"


class ConfigurationTypes(Enum):
    """
    Enumeration for different types of configurations for Philips Hue Entertainment areas.

    Each enum value represents a type of entertainment configuration, like screen, music, or 3D space setups.
    """

    SCREEN = "screen"
    MONITOR = "monitor"
    MUSIC = "music"
    THREEDSPACE = "3dspace"
    OTHER = "other"


class StatusTypes(Enum):
    """
    Enumeration for status types of Philips Hue Entertainment areas.

    Each enum value represents a status like active or inactive.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"


class ProxyMode(Enum):
    """
    Enumeration for the proxy modes available in the Philips Hue system.

    Each enum value represents a type of proxy mode like auto or manual.
    """

    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class Position:
    """
    Represents a 3D coordinate position.

    Attributes:
        x (float): The X coordinate.
        y (float): The Y coordinate.
        z (float): The Z coordinate.
    """

    x: float
    y: float
    z: float


@dataclass
class ResourceIdentifier:
    """
    Identifies a specific resource in the Philips Hue system.

    Attributes:
        rid (str): The resource identifier.
        rtype (ResourceTypes): The type of resource.
    """

    rid: str
    rtype: ResourceTypes


@dataclass
class SegmentReference:
    """
    Represents a reference to a segment of a resource.

    Attributes:
        service (ResourceIdentifier): The resource identifier.
        index (int): The index of the segment within the service.
    """

    service: ResourceIdentifier
    index: int


@dataclass
class EntertainmentChannel:
    """
    Represents a channel within a Philips Hue Entertainment area.

    Attributes:
        channel_id (int): The identifier of the channel.
        position (Position): The 3D position of the channel.
        members (list[SegmentReference]): The segments that are part of this channel.
    """

    channel_id: int
    position: Position
    members: list[SegmentReference]


@dataclass
class StreamProxyNode:
    """
    Represents a node in a stream proxy configuration.

    Attributes:
        rtype (ResourceTypes): The type of resource.
        rid (str): The resource identifier.
    """

    rtype: ResourceTypes
    rid: str


@dataclass
class StreamProxy:
    """
    Represents the stream proxy configuration.

    Attributes:
        mode (ProxyMode): The proxy mode.
        node (StreamProxyNode): The node of the stream proxy.
    """

    mode: ProxyMode
    node: StreamProxyNode


@dataclass
class ServiceLocation:
    """
    Represents the location of a service in a Philips Hue Entertainment area.

    Attributes:
        service (ResourceIdentifier): The resource identifier of the service.
        position (Optional[Position]): The primary position of the service.
        positions (list[Position]): Additional positions of the service.
        equalization_factor (float): The equalization factor for the service.
    """

    service: ResourceIdentifier
    position: Optional[Position]
    positions: list[Position]
    equalization_factor: float


@dataclass
class Locations:
    """
    Represents the locations of services in a Philips Hue Entertainment area.

    Attributes:
        service_locations (list[ServiceLocation]): A list of service locations.
    """

    service_locations: list[ServiceLocation]


class EntertainmentConfiguration:
    """
    Represents the configuration of a Philips Hue Entertainment area.

    This class encapsulates the various details of an Entertainment area, including its ID, type, status,
    configuration type, metadata, stream proxy settings, channels, locations, and light services. It offers
    functionality to convert this data into a dictionary format and to compare configurations.

    Attributes:
        id (str): Unique identifier of the Entertainment area.
        type (str): Type of the Entertainment area.
        id_v1 (Optional[str]): Version 1 identifier of the Entertainment area, if available.
        name (Optional[str]): Name of the Entertainment area.
        status (StatusTypes): Active status of the Entertainment area.
        configuration_type (ConfigurationTypes): Type of configuration for the Entertainment area.
        metadata (dict[str, Any]): Metadata associated with the Entertainment area.
        stream_proxy (StreamProxy): Stream proxy configuration for the Entertainment area.
        channels (list[EntertainmentChannel]): Channels in the Entertainment area.
        locations (Locations): Location configurations for the Entertainment area.
        light_services (list[ResourceIdentifier]): Light services associated with the Entertainment area.

    Methods:
        to_dict: Converts the EntertainmentConfiguration instance into a dictionary.
        __eq__: Compares this EntertainmentConfiguration instance with another object.

    This class is used to manage and represent the settings and configurations of a Philips Hue
    Entertainment area, particularly in context of entertainment setups like gaming, movies, or music.
    """

    #  pylint: disable=too-many-instance-attributes

    def __init__(self, data: dict[str, Any]):
        """
        Initializes the EntertainmentConfiguration with data provided in a dictionary format.

        Parameters:
            data (dict[str, Any]): A dictionary containing the various configuration details of the
            Entertainment area. Expected keys include 'id', 'type', 'status', 'configuration_type',
            'metadata', 'stream_proxy', 'channels', 'locations', and 'light_services'.
        """

        self.id = data["id"]
        self.type = data["type"]
        self.id_v1 = data.get("id_v1")
        self.name = data.get("name")
        self.status = StatusTypes(data["status"])
        self.configuration_type = ConfigurationTypes(data["configuration_type"])
        self.metadata = data["metadata"]

        proxy_data = data["stream_proxy"]
        self.stream_proxy = StreamProxy(
            mode=ProxyMode(proxy_data["mode"]),
            node=StreamProxyNode(
                rtype=ResourceTypes(proxy_data["node"]["rtype"]), rid=proxy_data["node"]["rid"]
            ),
        )

        self.channels = [
            EntertainmentChannel(
                channel_id=ch["channel_id"],
                position=Position(**ch["position"]),
                members=[
                    SegmentReference(
                        service=ResourceIdentifier(
                            rid=member["service"]["rid"],
                            rtype=ResourceTypes(member["service"]["rtype"]),
                        ),
                        index=member["index"],
                    )
                    for member in ch["members"]
                ],
            )
            for ch in data["channels"]
        ]

        self.locations = Locations(
            service_locations=[
                ServiceLocation(
                    service=ResourceIdentifier(
                        rid=loc["service"]["rid"], rtype=ResourceTypes(loc["service"]["rtype"])
                    ),
                    position=Position(**loc["position"]),
                    positions=[Position(**pos) for pos in loc["positions"]],
                    equalization_factor=loc["equalization_factor"],
                )
                for loc in data["locations"]["service_locations"]
            ]
        )

        self.light_services = [
            ResourceIdentifier(rid=ls["rid"], rtype=ResourceTypes(ls["rtype"]))
            for ls in data.get("light_services", [])
        ]

    def to_dict(self) -> dict[str, Any]:
        """
        Converts the EntertainmentConfiguration instance into a dictionary.

        This method enables the serialization of the EntertainmentConfiguration instance, making it
        easier to store or transmit its data.

        Returns:
            dict[str, Any]: A dictionary representation of the EntertainmentConfiguration instance.
        """

        return {
            "id": self.id,
            "type": self.type,
            "id_v1": self.id_v1,
            "name": self.name,
            "status": self.status.value,
            "configuration_type": self.configuration_type.value,
            "metadata": self.metadata,
            "stream_proxy": {
                "mode": self.stream_proxy.mode.value,
                "node": {
                    "rtype": self.stream_proxy.node.rtype.value,
                    "rid": self.stream_proxy.node.rid,
                },
            },
            "channels": [
                {
                    "channel_id": ch.channel_id,
                    "position": asdict(ch.position),
                    "members": [
                        {
                            "service": {
                                "rtype": member.service.rtype.value,
                                "rid": member.service.rid,
                            },
                            "index": member.index,
                        }
                        for member in ch.members
                    ],
                }
                for ch in self.channels
            ],
            "locations": {
                "service_locations": [
                    {
                        "service": {"rtype": loc.service.rtype.value, "rid": loc.service.rid},
                        "position": asdict(loc.position),
                        "positions": [asdict(pos) for pos in loc.positions],
                        "equalization_factor": loc.equalization_factor,
                    }
                    for loc in self.locations.service_locations
                ]
            },
            "light_services": [
                {"rtype": ls.rtype.value, "rid": ls.rid} for ls in self.light_services
            ],
        }

    def __eq__(self, other: Any) -> bool:
        """
        Compares this EntertainmentConfiguration instance with another object.

        This method checks if the provided object is an instance of EntertainmentConfiguration and
        compares their dictionary representations for equality.

        Parameters:
            other (Any): The object to compare with.

        Returns:
            bool: True if the other object is an instance of EntertainmentConfiguration and their
            dictionary representations are equal, False otherwise.
        """

        if not isinstance(other, EntertainmentConfiguration):
            return False
        return self.to_dict() == other.to_dict()
