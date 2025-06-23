from pydantic import BaseModel, ConfigDict


class BridgeApiHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    username: str
    clientkey: str
