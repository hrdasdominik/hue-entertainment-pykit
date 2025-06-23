import logging
import struct
from uuid import UUID

from hue_entertainment_pykit.lowl.enums.color_space_enum import ColorSpaceEnum
from hue_entertainment_pykit.lowl.models.light.light_base import LightBase
from hue_entertainment_pykit.lowl.utils.color_converter_util import ColorConverterUtil


logger = logging.getLogger(__name__)

class StreamingMessageBuilderUtil:
    """
    _DEFAULT_CHANNEL_VALUE (bytes): Default value for initializing streaming messages.
    """

    _DEFAULT_CHANNEL_VALUE = struct.pack(">B", 0x00)
    _PROTOCOL_NAME = "HueStream".encode("utf-8")
    _VERSION = struct.pack(">BB", 0x02, 0x00)
    _SEQUENCE_ID = struct.pack(">B", 0x01)
    _RESERVED = b"\x00\x00"
    _RESERVED2 = b"\x00"

    def __new__(cls, *args, **kwargs):
        raise TypeError("This class cannot be instantiated.")

    @staticmethod
    def build(entertainment_configuration_id: UUID, color_space: ColorSpaceEnum, channel_data_list: list[bytes]):
        """Constructs a message for streaming with the given channel data.

        Args:
            entertainment_configuration_id (str):
            color_space (ColorSpaceEnum):
            channel_data_list (list[bytes]): The channel data to be included in the message. It includes various
            parameters such as protocol name, version, sequence ID, reserved bytes, color space, and entertainment ID,
            concatenated with the actual channel data.

        Returns:
            bytes: The constructed message, ready to be sent over the network.
        """

        return b''.join([
            StreamingMessageBuilderUtil._PROTOCOL_NAME,
            StreamingMessageBuilderUtil._VERSION,
            StreamingMessageBuilderUtil._SEQUENCE_ID,
            StreamingMessageBuilderUtil._RESERVED,
            StreamingMessageBuilderUtil.encode_color_space(color_space),
            StreamingMessageBuilderUtil._RESERVED2,
            str(entertainment_configuration_id).encode("utf-8"),
            *channel_data_list
        ])

    @staticmethod
    def encode_color_space(color_space: ColorSpaceEnum) -> bytes:
        """
        Encodes the given color space into a single byte.

        Args:
            color_space (ColorSpaceEnum): The color space to encode.
                Expected values are 'rgb' or 'xyb'.

        Returns:
            bytes: A single byte where:
                - 0x00 represents the 'rgb' color space,
                - 0x01 represents the 'xyb' color space.
        """

        return struct.pack(">B", 0x00 if color_space.value == "rgb" else 0x01)

    @staticmethod
    def encode_light_data(light: LightBase) -> bytes:
        """
        Encodes a light object's ID and color values into bytes.

        Args:
            light (LightBase): The light object to encode,
                which must provide methods `get_id()` and `get_colors()`.

        Returns:
            bytes: A 7-byte sequence per channel containing:
                - 1 byte for the channel ID (0-19),
                - 6 bytes for the color values as three unsigned shorts (16-bit each), in either RGB or XY+Brightness order depending on the selected color space in the message header.
        """

        channel_data = b""
        channel_data += struct.pack(">B", light.get_entertainment_channel_id())

        rx, gy, b = ColorConverterUtil.xyb_or_rgb_to_16bit(light.get_colors())
        logger.debug("Encoding light colors (16-bit): %s %s %s", rx, gy, b)
        channel_data += struct.pack(">HHH", rx, gy, b)

        logger.debug("Encoded light data: %s", channel_data)
        return channel_data

    @staticmethod
    def init_message(entertainment_configuration_id: UUID) -> bytes:
        """Initialize the streaming message with default channel data.

        Returns:
            bytes: The initialized message.
        """

        x, y, b = ColorConverterUtil.xyb_or_rgb_to_16bit((0.0, 0.0, 0.0))

        channel_data = StreamingMessageBuilderUtil._DEFAULT_CHANNEL_VALUE
        channel_data += struct.pack(">HHH", x, y, b)

        return StreamingMessageBuilderUtil.build(entertainment_configuration_id, ColorSpaceEnum.XYB, [channel_data])
