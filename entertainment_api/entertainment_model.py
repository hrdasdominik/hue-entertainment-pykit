from dataclasses import dataclass
from typing import List, Optional

# Enum-like strings for rtype, replace with actual Enum if needed
ALLOWED_RTYPES = [
    "device", "bridge_home", "room", "zone", "light", "button",
    "relative_rotary",
    "temperature", "light_level", "motion", "camera_motion", "entertainment",
    "contact",
    "tamper", "grouped_light", "device_power", "zigbee_bridge_connectivity",
    "zigbee_connectivity",
    "zgp_connectivity", "bridge", "zigbee_device_discovery", "homekit",
    "matter", "matter_fabric",
    "scene", "entertainment_configuration", "public_image", "auth_v1",
    "behavior_script",
    "behavior_instance", "geofence", "geofence_client", "geolocation",
    "smart_scene"
]


@dataclass
class Segment:
    start: int  # Minimum: 0
    length: int  # Minimum: 1


@dataclass
class ResourceReference:
    rid: str  # Pattern: ^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$
    rtype: str  # One of the specified types


@dataclass
class Segments:
    configurable: bool
    max_segments: int  # Minimum: 1
    segments: List[Segment]  # MinItems: 1


@dataclass
class Entertainment:
    id: str  # Pattern: ^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$
    type: str  # 'entertainment'
    owner: ResourceReference
    renderer: bool
    proxy: bool
    equalizer: bool
    id_v1: Optional[str]  # Pattern: ^(\/[a-z]{4,32}\/[0-9a-zA-Z-]{1,32})?$
    renderer_reference: Optional[ResourceReference]
    max_streams: Optional[int]  # Minimum: 1
    segments: Optional[Segments]
