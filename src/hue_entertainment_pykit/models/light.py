from src.hue_entertainment_pykit.exceptions.not_valid_color import NotValidColor
from src.hue_entertainment_pykit.utils.color_validator import ColorValidator


class LightBase:
    def __init__(self, channel_id: int, light_name: str):
        self.__id = channel_id
        self.__name = light_name

    def get_id(self):
        return self.__id

    def get_colors(self):
        ...

    def set_colors(self, rx: int | float, gy: int | float, bb: int | float):
        ...


class LightRGB(LightBase):
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


class LightXYB(LightBase):
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
