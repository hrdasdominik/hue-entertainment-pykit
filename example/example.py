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

from hue_entertainment_pykit import Discovery, Streaming, Entertainment, setup_logs
from models.bridge import Bridge
from utils.logger import logging


def example():
    """Runs the example workflow for discovering bridges and managing streaming."""

    setup_logs()
    logging.info("Example started")
    discovery = Discovery()
    bridges: dict[str, Bridge] = discovery.discover_bridges()

    bridge = list(bridges.values())[0]

    entertainment_service = Entertainment(bridge)
    entertainment_configs = entertainment_service.get_entertainment_configs()

    entertainment_config = list(entertainment_configs.values())[0]

    streaming = Streaming(
        bridge,
        entertainment_config,
        entertainment_service.get_ent_conf_repo(),
    )

    streaming.setup_for_streaming()

    streaming.set_color_space("xyb")

    streaming.set_input((0.0, 0.63435, 0.3, 0))
    streaming.set_input((0.63435, 0.0, 0.3, 1))
    streaming.set_input((0.18725, 0.78634, 0.3, 2))
    streaming.set_input((0.63435, 0.87236, 0.3, 3))
    streaming.set_input((0.84682, 0.21238, 0.3, 4))
    streaming.set_input((0.32348, 0.20952, 0.3, 5))
    streaming.set_input((0.84395, 0.74395, 0.3, 6))

    time.sleep(0.1)

    streaming.setup_for_stop_streaming()
    logging.info("Example finished")


if __name__ == "__main__":
    example()
