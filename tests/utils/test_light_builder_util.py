import unittest
from types import SimpleNamespace
from uuid import UUID, uuid4
from unittest.mock import patch

from hue_entertainment_pykit.lowl.enums.color_space_enum import ColorSpaceEnum

import hue_entertainment_pykit.lowl.utils.light_builder_util as lbu


class DummyRGB:
    def __init__(self, _id, name, bridge_id, r, g, b, channel_id, config_id):
        self.id = _id
        self.name = name
        self.bridge_id = bridge_id
        self.r = r
        self.g = g
        self.b = b
        self.channel_id = channel_id
        self.config_id = config_id


class DummyXYB:
    def __init__(self, _id, name, bridge_id, x, y, brightness, channel_id, config_id):
        self.id = _id
        self.name = name
        self.bridge_id = bridge_id
        self.x = x
        self.y = y
        self.brightness = brightness
        self.channel_id = channel_id
        self.config_id = config_id


def make_light_hue(light_id: UUID, name: str, x: float, y: float, brightness: float):
    xy = SimpleNamespace(x=x, y=y)
    color = SimpleNamespace(xy=xy)
    dimming = SimpleNamespace(brightness=brightness)
    metadata = SimpleNamespace(name=name)
    return SimpleNamespace(id=light_id, color=color, dimming=dimming, metadata=metadata)


class TestLightBuilderUtil(unittest.TestCase):
    def test_build_rgb_path_returns_light_rgb_and_uses_converter(self):
        light_id = uuid4()
        bridge_id = uuid4()
        config_id = uuid4()
        name = "Hue Bulb"
        x, y = 0.25, 0.35
        channel_id = 2
        light_hue = make_light_hue(light_id, name, x, y, 87.5)

        with patch.object(lbu, "LightRGB", DummyRGB), \
             patch.object(lbu, "LightXYB", DummyXYB), \
             patch.object(lbu.ConverterUtil, "xyb_to_rgb8", return_value=(11, 22, 33)) as mock_conv:

            out = lbu.LightBuilderUtil.build(
                light_hue=light_hue,
                color_space=ColorSpaceEnum.RGB,
                entertainment_configuration_channel_id=channel_id,
                entertainment_configuration_id=config_id,
                bridge_id=bridge_id,
            )

        self.assertIsInstance(out, DummyRGB)
        self.assertEqual(out.id, light_id)
        self.assertEqual(out.name, name)
        self.assertEqual(out.bridge_id, bridge_id)
        self.assertEqual((out.r, out.g, out.b), (11, 22, 33))
        self.assertEqual(out.channel_id, channel_id)
        self.assertEqual(out.config_id, config_id)

        mock_conv.assert_called_once()
        args, _ = mock_conv.call_args
        self.assertEqual(len(args), 1)
        sent_tuple = args[0]
        self.assertIsInstance(sent_tuple[0], float)
        self.assertIsInstance(sent_tuple[1], float)
        self.assertEqual(float(sent_tuple[0]), x)
        self.assertEqual(float(sent_tuple[1]), y)

    def test_build_xyb_path_returns_light_xyb_and_converts_brightness_to_decimal(self):
        light_id = uuid4()
        bridge_id = uuid4()
        config_id = uuid4()
        name = "Hue Bulb 2"
        x, y = 0.4, 0.2
        brightness = 55.0
        channel_id = 0
        light_hue = make_light_hue(light_id, name, x, y, brightness)

        with patch.object(lbu, "LightRGB", DummyRGB), \
             patch.object(lbu, "LightXYB", DummyXYB):

            out = lbu.LightBuilderUtil.build(
                light_hue=light_hue,
                color_space=ColorSpaceEnum.XYB if hasattr(ColorSpaceEnum, "XYB") else ColorSpaceEnum.RGB,
                entertainment_configuration_channel_id=channel_id,
                entertainment_configuration_id=config_id,
                bridge_id=bridge_id,
            )

        self.assertIsInstance(out, DummyXYB)
        self.assertEqual(out.id, light_id)
        self.assertEqual(out.name, name)
        self.assertEqual(out.bridge_id, bridge_id)
        self.assertEqual((out.x, out.y), (x, y))
        self.assertIsInstance(out.brightness, float)
        self.assertEqual(brightness, out.brightness)
        self.assertEqual(out.channel_id, channel_id)
        self.assertEqual(out.config_id, config_id)


if __name__ == "__main__":
    unittest.main()