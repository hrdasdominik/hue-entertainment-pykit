from typing import Optional
from uuid import UUID

from hue_entertainment_pykit.lowl.exceptions.not_valid_color import NotValidColor
from hue_entertainment_pykit.lowl.models.light.light_base import LightBase
from hue_entertainment_pykit.lowl.utils.color_validator_util import ColorValidatorUtil


class LightRGB(LightBase):
    def __init__(self,
                 light_id: UUID,
                 light_name: str,
                 bridge_id: UUID,
                 r: int,
                 g: int,
                 b: int,
                 entertainment_configuration_channel_id: int,
                 entertainment_configuration_id: Optional[UUID] = None):
        super().__init__(light_id,
                         light_name,
                         bridge_id,
                         entertainment_configuration_channel_id,
                         entertainment_configuration_id)
        self.__r: int = r
        self.__g: int = g
        self.__b: int = b

    def get_colors(self) -> tuple[int, int, int]:
        return self.__r, self.__g, self.__b

    def set_colors(self, r: int, g: int, b: int):
        if not ColorValidatorUtil.is_valid_rgb((r, g, b)):
            raise NotValidColor("Each color must be between 0 and 255")

        self.__r: int = r
        self.__g: int = g
        self.__b: int = b

    def to_dict(self):
        base = super().to_dict()
        base.update({
            "r": self.__r,
            "g": self.__g,
            "b": self.__b
        })
        return base