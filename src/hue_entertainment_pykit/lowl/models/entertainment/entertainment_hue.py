from uuid import UUID

from pydantic import BaseModel, ConfigDict

from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference


class EntertainmentHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID
    renderer_reference: ResourceReference
