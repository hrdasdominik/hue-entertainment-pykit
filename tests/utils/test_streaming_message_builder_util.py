

import struct
import unittest
from types import SimpleNamespace
from uuid import UUID
from unittest.mock import patch

import hue_entertainment_pykit.lowl.utils.streaming_message_builder_util as sut


class _DummyLight:
    def __init__(self, channel_id, colors):
        self._cid = channel_id
        self._colors = colors

    def get_entertainment_channel_id(self):
        return self._cid

    def get_colors(self):
        return self._colors


class TestStreamingMessageBuilderUtil(unittest.TestCase):
    def test_class_is_not_instantiable(self):
        with self.assertRaises(TypeError):
            sut.StreamingMessageBuilderUtil()  # type: ignore[misc]

    def test_encode_color_space(self):
        rgb = SimpleNamespace(value="rgb")
        xyb = SimpleNamespace(value="xyb")
        self.assertEqual(sut.StreamingMessageBuilderUtil.encode_color_space(rgb), struct.pack(">B", 0x00))
        self.assertEqual(sut.StreamingMessageBuilderUtil.encode_color_space(xyb), struct.pack(">B", 0x01))

    def test_encode_light_data(self):
        light = _DummyLight(channel_id=5, colors=(0.1, 0.2, 0.3))
        with patch.object(sut.ConverterUtil, "xyb_or_rgb_to_16_bit", return_value=(1, 2, 3)):
            out = sut.StreamingMessageBuilderUtil.encode_light_data(light)
        self.assertEqual(out, struct.pack(">BHHH", 5, 1, 2, 3))

    def test_build_message_structure(self):
        uuid = UUID("12345678-1234-5678-1234-567812345678")
        rgb = SimpleNamespace(value="rgb")
        channels = [b"ABC", b"DEF"]
        msg = sut.StreamingMessageBuilderUtil.build(uuid, rgb, channels)

        expected = b"".join([
            b"HueStream",              # protocol
            b"\x02\x00",               # version
            b"\x01",                   # sequence id
            b"\x00\x00",               # reserved
            b"\x00",                   # color space rgb
            b"\x00",                   # reserved2
            str(uuid).encode("utf-8"),
            b"ABC",
            b"DEF",
        ])
        self.assertEqual(msg, expected)

    def test_init_message_uses_default_channel_and_xyb_header(self):
        fake_enum = SimpleNamespace(XYB=SimpleNamespace(value="xyb"))
        with patch.object(sut, "ColorSpaceEnum", fake_enum), \
             patch.object(sut.ConverterUtil, "xyb_or_rgb_to_16_bit", return_value=(0, 0, 0)):
            uuid = UUID("aaaaaaaa-bbbb-cccc-dddd-eeeeeeeeeeee")
            msg = sut.StreamingMessageBuilderUtil.init_message(uuid)

        self.assertTrue(msg.startswith(b"HueStream\x02\x00\x01\x00\x00"))
        self.assertEqual(msg[14], 0x01)
        self.assertEqual(msg[15], 0x00)
        self.assertIn(str(uuid).encode("utf-8"), msg)
        tail = msg[-7:]
        self.assertEqual(tail, b"\x00\x00\x00\x00\x00\x00\x00")


if __name__ == "__main__":
    unittest.main()