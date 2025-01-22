from src.hue_entertainment_pykit.exception.not_valid_color import NotValidColor
from src.hue_entertainment_pykit.light.light_abstract import LightAbstract
from src.hue_entertainment_pykit.utils.color_validator import ColorValidator


class LightRGB(LightAbstract):
    def __init__(self, channel_id: int, light_name: str, r: int, g: int, b: int):
        super().__init__(channel_id, light_name)
        self._r = r
        self._g = g
        self._b = b

    def get_colors(self):
        return self._r, self._g, self._b

    def set_colors(self, r: int, g: int, b: int):
        if not ColorValidator.is_valid_rgb8((r, g, b)):
            raise NotValidColor("Each color must be between 0 and 255")

        self._r = r
        self._g = g
        self._b = b