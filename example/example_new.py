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

from src.hue_entertainment_pykit_new import HueEntertainmentPyKit
from src.utils.logger import logging


def example():
    """Runs the example workflow for discovering bridges and managing streaming."""

    hue_pykit = HueEntertainmentPyKit()
    hue_pykit.modify_log_config(level=logging.WARNING)

    logging.info("Example started")

    bridge_dict = hue_pykit.get_all_bridges()
    hue_pykit.set_bridge(bridge_dict["1st Bridge"])

    configurations = hue_pykit.get_entertainment_configurations()
    hue_pykit.set_entertainment_configuration(configurations["43bcab07-e159-45bb-8760-59e347559319"])

    hue_pykit.start_stream()
    hue_pykit.set_color_space("xyb")

    hue_pykit.set_single_light([0.0, 0.18725, 1.0, 0])

    time.sleep(1.0)

    hue_pykit.set_group_lights([
        (0.0, 0.63435, 1.0, 0),
        (0.63435, 0.0, 1.0, 1),
        (0.18725, 0.78634, 1.0, 2)
    ])

    time.sleep(0.1)

    hue_pykit.stop_stream()
    logging.info("Example finished")


if __name__ == "__main__":
    example()
