from enum import Enum
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference


class Channel(BaseModel):
    model_config = ConfigDict(extra='ignore')
    channel_id: int
    members: list[ResourceReference]

class StatusTypes(Enum):
    """
    Enumeration for status types of Philips Hue Entertainment areas.

    Each enum value represents a status like active or inactive.
    """

    ACTIVE = "active"
    INACTIVE = "inactive"

class EntertainmentConfigurationHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID
    name: str
    status: StatusTypes
    channels: list[Channel]
    light_services: list[ResourceReference]
