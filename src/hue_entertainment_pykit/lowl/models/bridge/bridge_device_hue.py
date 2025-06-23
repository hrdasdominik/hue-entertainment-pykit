from uuid import UUID

from pydantic import BaseModel, ConfigDict

from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference, Metadata


class BridgeDeviceHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID
    metadata: Metadata
    services: list[ResourceReference]
