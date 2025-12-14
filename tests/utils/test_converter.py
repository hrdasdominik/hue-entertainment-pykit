"""
Module: test_converter.py

This module contains unit tests for the Converter class, focusing on testing the functionality of
converting color values between different formats used in light control and rendering.

Classes:
    TestConverter: A suite of unit tests for the Converter class.
"""

import unittest

from hue_entertainment_pykit.utils.converter import Converter


# pylint: disable=protected-access, attribute-defined-outside-init
class TestConverter(unittest.TestCase):
    """
    Test suite for the Converter class, which handles color conversions for light control applications.

    This class tests various color conversion methods, ensuring accurate transformations between
    different color formats and representations.
    """

    def test_normalize_rgb(self):
        """
        Tests the _normalize_rgb method to ensure correct normalization of RGB values to [0, 1] range.
        """

        result = Converter._normalize_rgb((255, 128, 0))
        expected = [1.0, 0.5019607843137255, 0.0]
        self.assertEqual(result, expected)

    def test_rgb8_to_rgb16(self):
        """
        Tests the rgb8_to_rgb16 method to verify conversion from 8-bit RGB to 16-bit RGB format.
        """

        result = Converter.rgb8_to_rgb16((255, 128, 0))
        expected = (65535, 32896, 0)
        self.assertEqual(result, expected)

    def test_rgb8_to_rgb16_various_inputs(self):
        """
        Tests the rgb8_to_rgb16 method with various input values to ensure accurate conversions.
        """

        test_cases = [
            ((0, 0, 0), (0, 0, 0)),
            ((255, 255, 255), (65535, 65535, 65535)),
            ((255, 0, 0), (65535, 0, 0)),
            ((0, 255, 0), (0, 65535, 0)),
            ((0, 0, 255), (0, 0, 65535)),
            ((123, 45, 67), (31611, 11565, 17219)),
        ]

        for rgb8, expected_rgb16 in test_cases:
            result = Converter.rgb8_to_rgb16(rgb8)
            self.assertEqual(result, expected_rgb16)

    def test_float_to_16bit(self):
        """
        Tests the xyb_to_rgb16 method to ensure correct conversion from float values to 16-bit values.
        """

        result = Converter.xyb_to_rgb16((0.0, 0.5, 1.0))
        expected = (0, 32767, 65535)
        self.assertEqual(result, expected)

    def test_int_to_hex(self):
        """
        Tests the int_to_hex method to verify conversion of integer values to hexadecimal strings.
        """

        result = Converter.int_to_hex(255)
        expected = "0xff"
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main()
