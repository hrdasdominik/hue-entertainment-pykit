from typing import Annotated
from uuid import UUID
from typing import Literal

from pydantic import Field, ConfigDict, BaseModel

from hue_entertainment_pykit.lowl.models.shared.classes import ResourceReference, Metadata


class XY(BaseModel):
    model_config = ConfigDict(extra='ignore')

    x: Annotated[float, Field(ge=0, le=1)]
    y: Annotated[float, Field(ge=0, le=1)]


class Color(BaseModel):
    model_config = ConfigDict(extra='ignore')

    xy: XY
    gamut_type: Literal['A', 'B', 'C'] = 'C'


class Dimming(BaseModel):
    model_config = ConfigDict(extra='ignore')

    brightness: Annotated[float, Field(ge=0, le=100.0)]


class LightHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID
    owner: ResourceReference
    metadata: Metadata
    color: Color
    dimming: Dimming
