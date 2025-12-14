"""
Contains the Converter class, offering utility functions for converting color values between different formats.
These include RGB to different bit depths, RGB to XYB color space conversions, and color normalizations.
The Converter class supports color manipulations for the Philips Hue lighting system, ensuring precise and
efficient color data handling.
"""


class Converter:
    """
    Provides utility functions for color value conversions between various formats such as RGB and XYB,
    used in lighting and color processing. This class is essential for accurate color manipulations within
    the Philips Hue system.
    """

    @staticmethod
    def _normalize_rgb(rgb8):
        """
        Normalize the RGB values from 0-255 range to 0-1 range.

        Parameters:
            rgb8 (tuple[int, int, int]): A tuple representing RGB values, where each value is in the range 0-255.

        Returns:
            list[float]: A list containing normalized RGB values in the range 0-1.
        """

        return [value / 255.0 for value in rgb8]

    @staticmethod
    def rgb8_to_rgb16(rgb8: tuple[int, int, int]):
        """
        Convert 8-bit RGB values to 16-bit RGB values.

        Parameters:
            rgb8 (tuple[int, int, int]): A tuple representing 8-bit RGB values.

        Returns:
            tuple[int, int, int]: A tuple representing the equivalent 16-bit RGB values.
        """

        return tuple(int(value * 65535) for value in Converter._normalize_rgb(rgb8))

    @staticmethod
    def xyb_to_rgb16(xyb: tuple[float, float, float]):
        """
        Converts XYB color values to 16-bit RGB values. The XYB format is used in lighting to represent
        color in terms of chromaticity and brightness.

        Parameters:
            xyb (tuple[float, float, float]): Color values in XYB format.

        Returns:
            tuple[int, int, int]: The equivalent 16-bit RGB values.
        """

        return tuple(int(max(0.0, min(1.0, value)) * float(65535)) for value in xyb)

    @staticmethod
    def int_to_hex(value: int):
        """
        Convert an integer value to its hexadecimal string representation.

        Parameters:
            value (int): The integer value to convert.

        Returns:
            str: The hexadecimal string representation of the value.
        """

        return f"0x{value:02x}"
