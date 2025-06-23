import json
from abc import ABC, abstractmethod
from typing import Any, Optional
from uuid import UUID

class LightBase(ABC):
    def __init__(self,
                 light_id: UUID,
                 light_name: str,
                 bridge_id: UUID,
                 entertainment_configuration_channel_id: int,
                 # TODO: myb add entertainment_id or service_id or rid
                 entertainment_configuration_id: Optional[UUID] = None):
        self.__light_id: UUID = light_id
        self.__name: str = light_name
        self.__bridge_id: UUID = bridge_id
        self.__entertainment_configuration_channel_id: int = entertainment_configuration_channel_id
        self.__entertainment_configuration_id: UUID = entertainment_configuration_id

    def get_entertainment_channel_id(self) -> int:
        return self.__entertainment_configuration_channel_id

    def get_light_id(self) -> UUID:
        return self.__light_id

    def get_light_name(self) -> str:
        return self.__name

    @abstractmethod
    def get_colors(self) -> tuple[int | float, int | float, int | float]:
        ...

    @abstractmethod
    def set_colors(self, rx: int | float, gy: int | float, b: int | float):
        ...

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.__light_id,
            "name": self.__name,
            "bridge_id": self.__bridge_id,
            "entertainment_configuration_id": self.__entertainment_configuration_id
        }

    def __repr__(self):
        return json.dumps(self.to_dict(), default=str)