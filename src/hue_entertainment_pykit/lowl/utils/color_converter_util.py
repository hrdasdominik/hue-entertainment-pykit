from hue_entertainment_pykit.lowl.exceptions.not_valid_color import NotValidColor
from hue_entertainment_pykit.lowl.utils.color_validator_util import ColorValidatorUtil


class ColorConverterUtil:
    MAX_RGB = 255
    MAX_16_BIT = 65535

    @staticmethod
    def _gamma_fwd(u: float) -> float:
        """Convert sRGB to linear RGB."""
        return ((u + 0.055) / 1.055) ** 2.4 if u > 0.04045 else u / 12.92

    @staticmethod
    def _gamma_inv(u: float) -> float:
        """Convert linear RGB to sRGB."""
        return 1.055 * (u ** (1.0 / 2.4)) - 0.055 if u > 0.0031308 else 12.92 * u

    @staticmethod
    def rgb8_to_xyb(rgb8: tuple[int, int, int]) -> tuple[float, float, float]:
        """
        Convert sRGB8 (0–255) to xyY (x, y, brightness Y).
        Returns x, y, and Y as floats.
        """
        if len(rgb8) != 3:
            raise ValueError(f"Expected (R, G, B). Got: {rgb8}")

        # Normalize and linearize
        r, g, b = [v / 255.0 for v in rgb8]
        r, g, b = (ColorConverterUtil._gamma_fwd(r),
                   ColorConverterUtil._gamma_fwd(g),
                   ColorConverterUtil._gamma_fwd(b))

        # RGB to XYZ (D65)
        X = r * 0.4124 + g * 0.3576 + b * 0.1805
        Y = r * 0.2126 + g * 0.7152 + b * 0.0722
        Z = r * 0.0193 + g * 0.1192 + b * 0.9505

        denom = X + Y + Z
        if denom == 0:
            x = y = 0.0
        else:
            x = X / denom
            y = Y / denom

        return x, y, Y

    @staticmethod
    def xyb_to_rgb8(xyb: tuple[float, float, float]) -> tuple[int, int, int]:
        """
        Convert xyY (x, y, brightness Y) to sRGB8 (0–255).
        """
        if len(xyb) != 3:
            raise ValueError(f"Expected (x, y, Y). Got: {xyb}")

        x, y, Y = xyb
        if y <= 0:
            return 0, 0, 0

        # xyY → XYZ
        z = 1.0 - x - y
        X = (Y / y) * x
        Z = (Y / y) * z

        # XYZ → linear RGB (D65)
        r_lin = 3.2406 * X - 1.5372 * Y - 0.4986 * Z
        g_lin = -0.9689 * X + 1.8758 * Y + 0.0415 * Z
        b_lin = 0.0557 * X - 0.2040 * Y + 1.0570 * Z

        # Clamp negatives
        r_lin, g_lin, b_lin = [max(0.0, c) for c in (r_lin, g_lin, b_lin)]

        # Normalize if necessary
        m = max(r_lin, g_lin, b_lin, 1.0)
        r_lin /= m
        g_lin /= m
        b_lin /= m

        # Linear → sRGB
        r, g, b = (ColorConverterUtil._gamma_inv(r_lin),
                   ColorConverterUtil._gamma_inv(g_lin),
                   ColorConverterUtil._gamma_inv(b_lin))

        # Convert to 8-bit integers
        def _to8(u: float) -> int:
            return int(round(max(0.0, min(1.0, u)) * ColorConverterUtil.MAX_RGB))

        return int(_to8(r)), int(_to8(g)), int(_to8(b))

    @staticmethod
    def rgb8_to_16bit(rgb8: tuple[int, int, int]) -> tuple[int, int, int]:
        """Expand 8-bit RGB (0–255) to 16-bit RGB (0–65535)."""
        return ((rgb8[0] << 8) | rgb8[0],
                (rgb8[1] << 8) | rgb8[1],
                (rgb8[2] << 8) | rgb8[2])

    @staticmethod
    def xyb_to_16bit(xyb: tuple[float, float, float]) -> tuple[int, int, int]:
        """Convert (xy,b) directly to 16-bit RGB."""
        return (
            int(round(max(0.0, min(1.0, xyb[0])) * 65535)),
            int(round(max(0.0, min(1.0, xyb[1])) * 65535)),
            int(round(max(0.0, min(1.0, xyb[2])) * 65535)),
        )

    @staticmethod
    def xyb_or_rgb_to_16bit(color: tuple[int, int, int] | tuple[float, float, float]) -> tuple[
        int, int, int]:
        if ColorValidatorUtil.is_valid_xyb(color):
            return ColorConverterUtil.xyb_to_16bit(color)
        elif ColorValidatorUtil.is_valid_rgb(color):
            return ColorConverterUtil.rgb8_to_16bit(color)
        else:
            raise NotValidColor("Color %s is neither valid RGB 8 or XYB type", color)

    @staticmethod
    def clamp_5dec(number: float) -> float:
        """
        Clamp float to 5 decimal places.
        If the float drifts beyond 5-decimal resolution due to floating-point math,
        snap it to the nearest valid step (±0.00001).
        """
        step = 1e-5
        rounded = round(number, 5)

        diff = number - rounded
        if abs(diff) >= step / 2:
            if diff > 0:
                rounded -= step
            else:
                rounded += step

        return max(0.0, min(1.0, rounded))