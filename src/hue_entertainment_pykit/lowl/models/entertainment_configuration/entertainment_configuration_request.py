from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field, ConfigDict

from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference, Position, Metadata
from hue_entertainment_pykit.lowl.models.shared.type_aliases_and_literals import (ProxyMode, EntertainmentType,
                                                                                  ConfigurationType)


class ServiceLocationPost(BaseModel):
    """Service + one or two positions."""
    model_config = ConfigDict(extra="forbid")

    service: ResourceReference
    positions: List[Position] = Field(..., min_length=1, max_length=2)


class StreamProxy(BaseModel):
    """Proxy configuration for the group."""
    model_config = ConfigDict(extra="forbid")

    mode: ProxyMode


class Locations(BaseModel):
    """Locations for entertainment services of the lights in the zone."""
    model_config = ConfigDict(extra="forbid")

    service_locations: List[ServiceLocationPost]


class EntertainmentConfigurationRequest(BaseModel):
    """
    Request body for creating/updating an entertainment configuration.
    Matches:
      - type: entertainment_configuration
      - metadata: object (opaque)
      - name: 1..32 chars
      - configuration_type: enum
      - stream_proxy: object with mode (auto only for now)
      - locations.service_locations: array of ServiceLocationPost
    """
    model_config = ConfigDict(extra="forbid")

    type: EntertainmentType = Field("entertainment_configuration")
    metadata: Metadata
    configuration_type: ConfigurationType
    stream_proxy: StreamProxy
    locations: Locations