from enum import Enum


class EndpointEnum(Enum):
    """Enum class for Philips Hue API endpoints"""

    API = "/api"
    API_CONFIG = "/api/config"
    AUTH_V1 = "/auth/v1"
    RESOURCE_BRIDGE = "/clip/v2/resource/bridge"
    RESOURCE_DEVICE = "/clip/v2/resource/device"
    RESOURCE_ENTERTAINMENT = "/clip/v2/resource/entertainment"
    RESOURCE_ENTERTAINMENT_CONFIGURATION = "/clip/v2/resource/entertainment_configuration"
    RESOURCE_LIGHT = "/clip/v2/resource/light"
