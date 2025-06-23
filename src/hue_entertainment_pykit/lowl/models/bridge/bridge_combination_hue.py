from ipaddress import IPv4Address
from typing import Optional

from pydantic import BaseModel, ConfigDict

from hue_entertainment_pykit.lowl.models.bridge.bridge_api_hue import BridgeApiHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_config_hue import BridgeConfigHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_device_hue import BridgeDeviceHue
from hue_entertainment_pykit.lowl.models.bridge.bridge_hue import BridgeHue


class BridgeCombinationHue(BaseModel):
    """
        Represents a Philips Hue Bridge instance with associated metadata and configuration.

        Attributes:
            ip_address (IPv4Address): The IPv4 address of the Hue Bridge.
            bridge (BridgeHue): Metadata and core data about the bridge itself, such as ID and name.
            device (BridgeDeviceHue): Information about the physical device hosting the bridge.
            config (BridgeConfigHue): Configuration settings for the bridge's API interface, including URLs and available services.
            type (Optional[str]): The type of the object, defaulting to 'bridge'. Useful for identification or serialization.
    """
    model_config = ConfigDict(extra='ignore')

    ip_address: IPv4Address
    bridge: BridgeHue
    device: BridgeDeviceHue
    config: BridgeConfigHue
    api: BridgeApiHue
    does_support_streaming: bool
    type: str = 'bridge'
