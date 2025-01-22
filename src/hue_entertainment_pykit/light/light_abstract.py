from abc import abstractmethod, ABC

from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import EntertainmentChannel
from src.hue_entertainment_pykit.light.light import Light


class LightAbstract(ABC):
    def __init__(self, channel_id: int, light_name: str):
        self.__id: int = channel_id
        self.__name: str = light_name
        self.__transition_time: float = 0.0

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    @abstractmethod
    def get_colors(self):
        ...

    @abstractmethod
    def set_colors(self, rx: int | float, gy: int | float, bb: int | float):
        ...

    def get_transition_time(self):
        return self.__transition_time

    def set_transition_time(self, transition_time: float):
        self.__transition_time = transition_time

    @staticmethod
    def transform_hue_light_to_light_model(entertainment_channel: EntertainmentChannel, light: Light):
        ...
