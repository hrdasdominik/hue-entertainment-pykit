from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.light.light_api_service import LightApiService


class LightService:
    def __init__(self, bridge: Bridge):
        self._light_api_service = LightApiService(bridge)

    def get_by_id(self, identification: str):
        return self._light_api_service.fetch_by_id(identification)

    def get_all(self):
        return self._light_api_service.fetch_all()

    def update(self, data):
        self._light_api_service.put(data)