from typing import Optional
from uuid import UUID

from hue_entertainment_pykit.lowl.exceptions.not_valid_color import NotValidColor
from hue_entertainment_pykit.lowl.models.light.light_base import LightBase
from hue_entertainment_pykit.lowl.utils.color_validator_util import ColorValidatorUtil


class LightXYB(LightBase):
    def __init__(self,
                 light_id: UUID,
                 light_name: str,
                 bridge_id: UUID,
                 x: float,
                 y: float,
                 brightness: float,
                 entertainment_configuration_channel_id: int,
                 entertainment_configuration_id: Optional[UUID] = None):
        super().__init__(light_id,
                         light_name,
                         bridge_id,
                         entertainment_configuration_channel_id,
                         entertainment_configuration_id)
        self.__x: float = x
        self.__y: float = y
        self.__brightness: float = brightness

    def get_colors(self) -> tuple[float, float, float]:
        return self.__x, self.__y, self.__brightness

    def set_colors(self, x: float, y: float, brightness: float | int):
        if isinstance(brightness, int):
            brightness = float(brightness)

        if not ColorValidatorUtil.is_valid_xyb((x, y, brightness)):
            raise NotValidColor("Each color must be between 0.0 and 1.0")

        self.__x: float = x
        self.__y: float = y
        self.__brightness: float = brightness

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "x": self.__x,
            "y": self.__y,
            "brightness": self.__brightness
        })
        return base
