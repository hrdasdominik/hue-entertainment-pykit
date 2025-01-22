"""
This script demonstrates how to use the Discovery, EntertainmentService, and
Streaming classes from the hue_entertainment_pykit. It performs the following steps:

1. Discovers bridges in the network.
2. Selects a bridge and retrieves the first entertainment configuration.
3. Initializes streaming with the selected bridge and entertainment configuration.
4. Starts the streaming service and sets the color space.
5. Sends multiple input commands to the streaming service.
6. Stops the streaming service after a brief pause.
"""
import time
from decimal import Decimal

from src.hue_entertainment_pykit.hue_entertainment_pykit import HueEntertainmentPyKit
from src.hue_entertainment_pykit.light.light_xyb import LightXYB
from src.hue_entertainment_pykit.utils.color_space_enum import ColorSpaceEnum
from src.hue_entertainment_pykit.utils.logger import logging


def example():
    """Runs the example workflow for discovering bridges and managing streaming."""

    hue_pykit = HueEntertainmentPyKit("example_new#test")
    hue_pykit.modify_log_config(level=logging.DEBUG)

    logging.info("Example started")

    bridge_name_list = hue_pykit.get_bridge_name_list()
    entertainment_configuration_name_list = hue_pykit.get_entertainment_configuration_name_list(bridge_name_list[0])

    hue_pykit.set_active_entertainment_configuration_on_bridge(bridge_name_list[0], entertainment_configuration_name_list[0])

    light_list = hue_pykit.get_light_list_from_bridge(bridge_name_list[0])

    hue_pykit.start_streaming_on_all_bridges()

    hue_pykit.set_color_space(ColorSpaceEnum.XYB)

    color = Decimal("0.0")
    for _ in range(10):
        logging.info(f"Color space: {color}")
        if color > 1.0:
            break

        for light in light_list:
            light.set_colors(float(color), float(color), 1.0)

        hue_pykit.set_color_and_brightness(bridge_name_list[0], light_list)
        color += Decimal("0.1")
        time.sleep(0.1)

    hue_pykit.stop_streaming_on_all_bridges()
    logging.info("Example finished")


if __name__ == "__main__":
    example()
