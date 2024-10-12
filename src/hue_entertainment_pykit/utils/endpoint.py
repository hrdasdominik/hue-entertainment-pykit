from enum import Enum


class Endpoint(Enum):
    """Enum class for Philips Hue API endpoints"""


    ENTERTAINMENT = "/clip/v2/resource/entertainment"
    API = "/api"
    CONFIG = "/api/config"
    AUTH_V1 = "/auth/v1"
    DEVICE = "/clip/v2/resource/device"
    BRIDGE = "/clip/v2/resource/bridge"
