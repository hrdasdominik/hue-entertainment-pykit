from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference


class DeviceHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID
    services: list[ResourceReference]

