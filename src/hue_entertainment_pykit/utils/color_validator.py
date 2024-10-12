class ColorValidator:
    @classmethod
    def is_user_input_valid(cls, user_input):
        rx, gy, bb, light_id = user_input
        color = rx, gy, bb

        if not cls.is_valid_rgb8(color) and not cls.is_valid_xyb(color):
            raise ValueError(
                "Invalid input: values must be a valid rgb8 (0 - 255) or xyb (0.0 - 1.0)"
            )

    @classmethod
    def is_valid_rgb8(cls, rgb8: tuple[int, int, int]) -> bool:
        """Check if the given RGB8 color is valid.

        Args:
            rgb8 (tuple[int, int, int]): A tuple representing the RGB8 color.

        Returns:
            bool: True if the color is a valid RGB8, False otherwise.
        """

        return all(0 <= value <= 255 for value in rgb8)

    @classmethod
    def is_valid_xyb(cls, xyb: tuple[float, float, float]) -> bool:
        """Check if the given XYB color is valid.

        Args:
            xyb (tuple[float, float, float]): A tuple representing the XYB color.

        Returns:
            bool: True if the color is a valid XYB, False otherwise.
        """

        return all(0.0 <= value <= 1.0 for value in xyb)
