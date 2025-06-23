from pydantic import BaseModel, ConfigDict


class BridgeConfigHue(BaseModel):
    model_config = ConfigDict(extra='ignore')

    swversion: str
    bridgeid: str