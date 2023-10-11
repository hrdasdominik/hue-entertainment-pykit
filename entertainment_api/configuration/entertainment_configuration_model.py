from dataclasses import dataclass, asdict
from enum import Enum
from typing import List, Optional, Dict, Any


class ResourceTypes(Enum):
    ENTERTAINMENT = "entertainment"
    LIGHT = "light"
    # Add other resource types here...


class ConfigurationTypes(Enum):
    SCREEN = "screen"
    MONITOR = "monitor"
    MUSIC = "music"
    THREEDSPACE = "3dspace"
    OTHER = "other"


class StatusTypes(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"


class ProxyMode(Enum):
    AUTO = "auto"
    MANUAL = "manual"


@dataclass
class Position:
    x: float
    y: float
    z: float


@dataclass
class ResourceIdentifier:
    rid: str
    rtype: ResourceTypes


@dataclass
class SegmentReference:
    service: ResourceIdentifier
    index: int


@dataclass
class EntertainmentChannel:
    channel_id: int
    position: Position
    members: List[SegmentReference]


@dataclass
class StreamProxyNode:
    rtype: ResourceTypes
    rid: str


@dataclass
class StreamProxy:
    mode: ProxyMode
    node: StreamProxyNode


@dataclass
class ServiceLocation:
    service: ResourceIdentifier
    position: Optional[Position]
    positions: List[Position]
    equalization_factor: float


@dataclass
class Locations:
    service_locations: List[ServiceLocation]


class EntertainmentConfiguration:

    def __init__(self, data: Dict[str, Any]):
        self.id = data['id']

        self.type = data['type']

        self.id_v1 = data.get('id_v1')

        self.name = data.get('name')

        self.status = StatusTypes(data['status'])

        self.configuration_type = ConfigurationTypes(data['configuration_type'])

        self.metadata = data['metadata']

        # Initialize stream_proxy

        proxy_data = data['stream_proxy']

        self.stream_proxy = StreamProxy(

            mode=ProxyMode(proxy_data['mode']),

            node=StreamProxyNode(

                rtype=ResourceTypes(proxy_data['node']['rtype']),

                rid=proxy_data['node']['rid']

            )

        )

        # Initialize channels

        self.channels = [

            EntertainmentChannel(

                channel_id=ch['channel_id'],

                position=Position(**ch['position']),

                members=[

                    SegmentReference(

                        service=ResourceIdentifier(

                            rid=member['service']['rid'],

                            rtype=ResourceTypes(member['service']['rtype'])

                        ),

                        index=member['index']

                    )

                    for member in ch['members']

                ]

            )

            for ch in data['channels']

        ]

        # Initialize locations

        self.locations = Locations(

            service_locations=[

                ServiceLocation(

                    service=ResourceIdentifier(

                        rid=loc['service']['rid'],

                        rtype=ResourceTypes(loc['service']['rtype'])

                    ),

                    position=Position(**loc['position']),

                    positions=[Position(**pos) for pos in loc['positions']],

                    equalization_factor=loc['equalization_factor']

                )

                for loc in data['locations']['service_locations']

            ]

        )

        # Initialize light_services

        self.light_services = [

            ResourceIdentifier(

                rid=ls['rid'],

                rtype=ResourceTypes(ls['rtype'])

            )

            for ls in data.get('light_services', [])

        ]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'type': self.type,
            'id_v1': self.id_v1,
            'name': self.name,
            'status': self.status.value,
            'configuration_type': self.configuration_type.value,
            'metadata': self.metadata,
            'stream_proxy': {
                'mode': self.stream_proxy.mode.value,
                'node': {
                    'rtype': self.stream_proxy.node.rtype.value,
                    'rid': self.stream_proxy.node.rid
                }
            },
            'channels': [
                {
                    'channel_id': ch.channel_id,
                    'position': asdict(ch.position),
                    'members': [
                        {
                            'service': {
                                'rtype': member.service.rtype.value,
                                'rid': member.service.rid
                            },
                            'index': member.index
                        }
                        for member in ch.members
                    ]
                }
                for ch in self.channels
            ],
            'locations': {
                'service_locations': [
                    {
                        'service': {
                            'rtype': loc.service.rtype.value,
                            'rid': loc.service.rid
                        },
                        'position': asdict(loc.position),
                        'positions': [asdict(pos) for pos in loc.positions],
                        'equalization_factor': loc.equalization_factor
                    }
                    for loc in self.locations.service_locations
                ]
            },
            'light_services': [
                {
                    'rtype': ls.rtype.value,
                    'rid': ls.rid
                }
                for ls in self.light_services
            ]
        }

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, EntertainmentConfiguration):
            return False
        return self.to_dict() == other.to_dict()

