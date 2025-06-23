from uuid import UUID

from hue_entertainment_pykit.lowl.enums.color_space_enum import ColorSpaceEnum
from hue_entertainment_pykit.lowl.models.light.light_base import LightBase
from hue_entertainment_pykit.lowl.models.light.light_hue import LightHue
from hue_entertainment_pykit.lowl.models.light.light_rgb import LightRGB
from hue_entertainment_pykit.lowl.models.light.light_xyb import LightXYB
from hue_entertainment_pykit.lowl.utils.color_converter_util import ColorConverterUtil


class LightBuilderUtil:
    @staticmethod
    def build(light_hue: LightHue,
              color_space: ColorSpaceEnum,
              entertainment_configuration_channel_id: int,
              entertainment_configuration_id: UUID,
              bridge_id: UUID) -> LightBase:
        if color_space == ColorSpaceEnum.RGB:
            xyb = light_hue.color.xy.x, light_hue.color.xy.y, light_hue.dimming.brightness
            rgb = ColorConverterUtil.xyb_to_rgb8(xyb)
            return LightRGB(light_hue.id,
                            light_hue.metadata.name,
                            bridge_id,
                            rgb[0],
                            rgb[1],
                            rgb[2],
                            entertainment_configuration_channel_id,
                            entertainment_configuration_id)
        else:
            return LightXYB(light_hue.id,
                            light_hue.metadata.name,
                            bridge_id,
                            light_hue.color.xy.x,
                            light_hue.color.xy.y,
                            light_hue.dimming.brightness / 100,
                            entertainment_configuration_channel_id,
                            entertainment_configuration_id)
