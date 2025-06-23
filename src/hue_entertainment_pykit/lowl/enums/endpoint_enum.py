from enum import Enum


class EndpointEnum(Enum):
    """Enum class for Philips Hue API endpoints"""


    ENTERTAINMENT = "clip/v2/resource/entertainment"
    ENTERTAINMENT_CONFIGURATION = "clip/v2/resource/entertainment_configuration"
    API = "api"
    CONFIG = "api/config"
    DEVICE = "clip/v2/resource/device"
    BRIDGE = "clip/v2/resource/bridge"
    LIGHT = "clip/v2/resource/light"
