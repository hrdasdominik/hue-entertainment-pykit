from dataclasses import dataclass, field
from typing import List, Literal, Optional
import re

@dataclass
class Node:
    rid: str
    rtype: Literal['device', 'bridge_home', 'room', 'zone', 'service_group', 'light', 'button',
                   'relative_rotary', 'temperature', 'light_level', 'motion', 'camera_motion',
                   'entertainment', 'contact', 'tamper', 'grouped_light', 'grouped_motion',
                   'grouped_light_level', 'device_power', 'device_software_update',
                   'zigbee_bridge_connectivity', 'zigbee_connectivity', 'zgp_connectivity',
                   'remote_access', 'bridge', 'zigbee_device_discovery', 'system_update', 'homekit',
                   'matter', 'matter_fabric', 'scene', 'entertainment_configuration', 'public_image',
                   'auth_v1', 'behavior_script', 'behavior_instance', 'geofence', 'geofence_client',
                   'geolocation', 'smart_scene']

    def __post_init__(self):
        if not re.match(r'^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$', self.rid):
            raise ValueError("Invalid rid format")

    def to_dict(self) -> dict:
        return {
            "rid": self.rid,
            "rtype": self.rtype
        }

@dataclass
class StreamProxy:
    mode: Literal['auto', 'manual']
    node: Optional[Node] = None

    def to_dict(self) -> dict:
        return {
            "mode": self.mode,
            "node": self.node.to_dict() if self.node else None
        }

@dataclass
class Position:
    x: float
    y: float
    z: float

    def __post_init__(self):
        if not (-1 <= self.x <= 1 and -1 <= self.y <= 1 and -1 <= self.z <= 1):
            raise ValueError("Coordinates must be between -1 and 1")

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }

@dataclass
class ServiceLocation:
    rid: str
    rtype: Literal['device', 'bridge_home', 'room', 'zone', 'service_group', 'light', 'button',
                   'relative_rotary', 'temperature', 'light_level', 'motion', 'camera_motion',
                   'entertainment', 'contact', 'tamper', 'grouped_light', 'grouped_motion',
                   'grouped_light_level', 'device_power', 'device_software_update',
                   'zigbee_bridge_connectivity', 'zigbee_connectivity', 'zgp_connectivity',
                   'remote_access', 'bridge', 'zigbee_device_discovery', 'system_update', 'homekit',
                   'matter', 'matter_fabric', 'scene', 'entertainment_configuration', 'public_image',
                   'auth_v1', 'behavior_script', 'behavior_instance', 'geofence', 'geofence_client',
                   'geolocation', 'smart_scene']
    positions: List[Position] = field(default_factory=list)

    def __post_init__(self):
        if len(self.positions) < 1 or len(self.positions) > 2:
            raise ValueError("positions must contain between 1 and 2 Position objects")

    def to_dict(self) -> dict:
        return {
            "rid": self.rid,
            "rtype": self.rtype,
            "positions": [position.to_dict() for position in self.positions]
        }

@dataclass
class Locations:
    service_locations: List[ServiceLocation] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "service_locations": [service_location.to_dict() for service_location in self.service_locations]
        }

@dataclass
class EntertainmentConfigurationCreateRequest:
    type: Literal['entertainment_configuration']
    metadata: dict
    configuration_type: Literal['screen', 'monitor', 'music', '3dspace', 'other']
    locations: Locations
    stream_proxy: Optional[StreamProxy] = None

    def __post_init__(self):
        if 'name' not in self.metadata or not (1 <= len(self.metadata['name']) <= 32):
            raise ValueError("metadata.name must be a string between 1 and 32 characters")

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "metadata": self.metadata,
            "configuration_type": self.configuration_type,
            "locations": self.locations.to_dict(),
            "stream_proxy": self.stream_proxy.to_dict() if self.stream_proxy else None
        }
