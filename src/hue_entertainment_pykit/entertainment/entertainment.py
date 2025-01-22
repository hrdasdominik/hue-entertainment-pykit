"""
This module provides a representation of the Philips Hue Entertainment model.

It includes dataclasses for defining resource identifiers, segments, and the overall Entertainment configuration.
These classes ensure strict validation and adherence to the Philips Hue API specifications for Entertainment areas.

Classes:
- EntertainmentResponse: Top-level structure that can hold "errors" and "data" lists.
- EntertainmentData: Represents a single Entertainment configuration item in "data".
- Segment: Represents a segment of a device used for entertainment purposes.
- Segments: Represents the segmentation configuration for a device.
- RendererReference: Represents a reference to a renderer service in the entertainment system.
- Owner: Represents the owner of a resource.
- Entertainment: Represents the main Entertainment configuration.

Example Usage:
    # Parsing the JSON structure into Python dataclasses might look like:
    #
    #   response_dict = json.loads(json_string)
    #   entertainment_response = EntertainmentResponse(
    #       errors = response_dict.get("errors", []),
    #       data = [
    #           EntertainmentData(
    #               **item
    #           ) for item in response_dict.get("data", [])
    #       ]
    #   )
    #
    #   # The nested __post_init__ validations will raise ValueError if anything is invalid.
    #
"""

import re
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Segment:
    """
    Represents a segment of a device used for entertainment purposes.

    Attributes:
        start (int): Start index of the segment (must be >= 0).
        length (int): Length of the segment (must be >= 1).
    """
    start: int
    length: int

    def __post_init__(self):
        if self.start < 0:
            raise ValueError(f"Segment.start must be >= 0, got {self.start}")
        if self.length < 1:
            raise ValueError(f"Segment.length must be >= 1, got {self.length}")

@dataclass
class Segments:
    """
    Represents the segmentation configuration for a device.

    Attributes:
        configurable (bool): Whether the segmentation is configurable.
        max_segments (int): Maximum number of segments allowed (must be >= 1).
        segments (List[Segment]): List of segments (must contain at least one segment).
    """
    configurable: bool
    max_segments: int
    segments: List[Segment]

    def __post_init__(self):
        if self.max_segments < 1:
            raise ValueError(f"Segments.max_segments must be >= 1, got {self.max_segments}")
        if not self.segments:
            raise ValueError("Segments.segments must contain at least one Segment")

@dataclass
class RendererReference:
    """
    Represents a reference to a renderer service in the entertainment system.

    Attributes:
        rid (str): Resource identifier (UUID) of the renderer.
        rtype (str): Type of the resource (e.g. 'light').
    """
    rid: str
    rtype: str

    def __post_init__(self):
        uuid_regex = r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$"
        if not re.match(uuid_regex, self.rid, re.IGNORECASE):
            raise ValueError(f"RendererReference.rid must be a valid UUID, got '{self.rid}'")

        valid_rtypes = {
            "device", "bridge_home", "room", "zone", "light",
            "service_group", "entertainment", "scene", "grouped_light"
        }
        if self.rtype not in valid_rtypes:
            raise ValueError(f"RendererReference.rtype must be one of {valid_rtypes}, got '{self.rtype}'")

@dataclass
class Owner:
    """
    Represents the owner of a resource (e.g., a device).

    Attributes:
        rid (str): Resource identifier (UUID) of the owner.
        rtype (str): Type of the owner resource (e.g. 'device').
    """
    rid: str
    rtype: str

    def __post_init__(self):
        uuid_regex = r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$"
        if not re.match(uuid_regex, self.rid, re.IGNORECASE):
            raise ValueError(f"Owner.rid must be a valid UUID, got '{self.rid}'")

        # Validate rtype (shortened list for demonstration)
        valid_rtypes = {
            "device", "light", "entertainment", "bridge_home", "room",
            "scene", "grouped_light", "service_group"
        }
        if self.rtype not in valid_rtypes:
            raise ValueError(f"Owner.rtype must be one of {valid_rtypes}, got '{self.rtype}'")

@dataclass
class Entertainment:
    """
    Represents the main Entertainment configuration.

    Attributes:
        type (str): Resource type (always "entertainment").
        id (str): Unique identifier (UUID) of the Entertainment configuration.
        id_v1 (Optional[str]): Optional version 1 identifier (e.g. "/lights/3").
        owner (Owner): The owning device or resource.
        renderer (bool): Indicates if the device can function as a renderer.
        renderer_reference (Optional[RendererReference]): Reference to the renderer service.
        proxy (bool): Indicates if the device can function as a proxy.
        equalizer (bool): Indicates if the device supports equalization.
        segments (Optional[Segments]): Segmentation configuration.
    """
    type: str = field(default="entertainment", init=False)
    id: str = field(default="")
    id_v1: Optional[str] = None
    owner: Owner = field(default=None)
    renderer: bool = False
    renderer_reference: Optional[RendererReference] = None
    proxy: bool = False
    equalizer: bool = False
    segments: Optional[Segments] = None

    def __post_init__(self):
        if self.type != "entertainment":
            raise ValueError(f"Entertainment.type must be 'entertainment', got '{self.type}'")

        uuid_regex = r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$"
        if not re.match(uuid_regex, self.id, re.IGNORECASE):
            raise ValueError(f"Entertainment.id must be a valid UUID, got '{self.id}'")

        if self.id_v1 and not self.id_v1.startswith("/lights/"):
            raise ValueError("Entertainment.id_v1 must start with '/lights/' if provided")

        if self.owner is None:
            raise ValueError("Entertainment.owner is required and cannot be None")
