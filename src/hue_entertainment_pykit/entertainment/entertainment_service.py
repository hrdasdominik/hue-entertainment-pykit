from src.hue_entertainment_pykit.bridge.bridge import Bridge
from src.hue_entertainment_pykit.entertainment.entertainment import Entertainment
from src.hue_entertainment_pykit.entertainment.entertainment_api_service import EntertainmentApiService


class EntertainmentService:
    def __init__(self, bridge: Bridge):
        self._bridge = bridge
        self._entertainment_api_service = EntertainmentApiService(bridge)

    def get_all_entertainments(self) -> dict[str, Entertainment]:
        return self._entertainment_api_service.fetch_all()

    def get_entertainment_by_id(self, entertainment_id: str) -> Entertainment:
        return self._entertainment_api_service.fetch_by_id(entertainment_id)
