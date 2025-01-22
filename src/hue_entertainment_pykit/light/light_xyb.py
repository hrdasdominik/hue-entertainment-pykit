from src.hue_entertainment_pykit.entertainment_configuration.entertainment_configuration import EntertainmentChannel
from src.hue_entertainment_pykit.exception.not_valid_color import NotValidColor
from src.hue_entertainment_pykit.light.light import Light
from src.hue_entertainment_pykit.light.light_abstract import LightAbstract
from src.hue_entertainment_pykit.utils.color_validator import ColorValidator


class LightXYB(LightAbstract):
    def __init__(self, channel_id: int, light_name: str, x: float, y: float, brightness: float):
        super().__init__(channel_id, light_name)
        self._x = x
        self._y = y
        self._brightness = brightness

    def get_colors(self):
        return self._x, self._y, self._brightness

    def set_colors(self, x: float, y: float, brightness: float):
        if not ColorValidator.is_valid_xyb((x, y, brightness)):
            raise NotValidColor("Each color must be between 0.0 and 1.0")

        self._x = x
        self._y = y
        self._brightness = brightness

    @staticmethod
    def transform_hue_light_to_light_model(entertainment_channel: EntertainmentChannel, light: Light):
        return LightXYB(
            entertainment_channel.channel_id,
            light.metadata.get("name"),
            entertainment_channel.position.x,
            entertainment_channel.position.y,
            entertainment_channel.position.z
        )
