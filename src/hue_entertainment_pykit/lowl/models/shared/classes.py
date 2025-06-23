from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from hue_entertainment_pykit.lowl.models.shared.type_aliases_and_literals import RType, RidPattern


class ResourceReference(BaseModel):
    model_config = ConfigDict(extra='ignore')
    rid: UUID = Field(..., description="UUID of referenced resource")
    rtype: RType = Field(..., description="Type of referenced resource")

class Position(BaseModel):
    """A 3D coordinate in normalized space [-1, 1]."""
    model_config = ConfigDict(extra="forbid")

    x: float = Field(..., ge=-1, le=1)
    y: float = Field(..., ge=-1, le=1)
    z: float = Field(..., ge=-1, le=1)

class Metadata(BaseModel):
    """ """
    model_config = ConfigDict(extra="ignore")

    name: str = Field(..., min_length=1, max_length=32, description="Friendly name")
