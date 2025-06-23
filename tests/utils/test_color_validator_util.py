import unittest

from hue_entertainment_pykit.lowl.utils.color_validator_util import ColorValidatorUtil


class TestColorValidatorUtil(unittest.TestCase):
    def test_is_valid_rgb_true_for_valid_values(self):
        self.assertTrue(ColorValidatorUtil.is_valid_rgb((0, 0, 0)))
        self.assertTrue(ColorValidatorUtil.is_valid_rgb((255, 255, 255)))
        self.assertTrue(ColorValidatorUtil.is_valid_rgb((12, 128, 254)))

    def test_is_valid_rgb_false_for_out_of_range(self):
        self.assertFalse(ColorValidatorUtil.is_valid_rgb((-1, 0, 0)))
        self.assertFalse(ColorValidatorUtil.is_valid_rgb((0, 256, 0)))
        self.assertFalse(ColorValidatorUtil.is_valid_rgb((0, 0, 999)))

    def test_is_valid_xyb_true_for_valid_values(self):
        self.assertTrue(ColorValidatorUtil.is_valid_xyb((0.0, 0.0, 0.0)))
        self.assertTrue(ColorValidatorUtil.is_valid_xyb((1.0, 1.0, 1.0)))
        self.assertTrue(ColorValidatorUtil.is_valid_xyb((0.12, 0.34, 0.56)))

    def test_is_valid_xyb_false_for_out_of_range(self):
        self.assertFalse(ColorValidatorUtil.is_valid_xyb((-0.01, 0.5, 0.5)))
        self.assertFalse(ColorValidatorUtil.is_valid_xyb((0.0, 1.01, 0.0)))
        self.assertFalse(ColorValidatorUtil.is_valid_xyb((0.0, 0.0, 2.0)))

    def test_is_user_input_valid_accepts_rgb8(self):
        ColorValidatorUtil.is_user_input_valid((12, 34, 56, 'light-1'))

    def test_is_user_input_valid_accepts_xyb(self):
        ColorValidatorUtil.is_user_input_valid((0.2, 0.4, 0.8, 'light-2'))

    def test_is_user_input_valid_raises_for_invalid(self):
        with self.assertRaises(ValueError):
            ColorValidatorUtil.is_user_input_valid((-1, 0, 0, 'light-3'))
        with self.assertRaises(ValueError):
            ColorValidatorUtil.is_user_input_valid((-0.1, 0.1, 0.2, 'light-4'))


if __name__ == '__main__':
    unittest.main()