from uuid import UUID

from pydantic import BaseModel, ConfigDict


class Owner(BaseModel):
    model_config = ConfigDict(extra='ignore')

    rid: UUID

class BridgeHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    id: UUID
    owner: Owner
    bridge_id: str