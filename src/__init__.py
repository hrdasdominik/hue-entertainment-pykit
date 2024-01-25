"""
The `hue_entertainment_pykit` module offers a suite of tools designed to interface with
Philips Hue Entertainment capabilities. It provides high-level abstractions to discover and interact with Hue bridges,
manage entertainment configurations, and create responsive lighting experiences.

Available Classes and Functions:
- `Discovery`: A utility class to discover Hue bridges on the local network. It simplifies the process of finding and
connecting to available Hue bridges without needing to deal with network details.
- `Streaming`: Facilitates the creation of entertainment sessions, allowing for the control of Hue lights in real-time
for dynamic lighting effects synchronized with media or games.
- `create_bridge`: A factory function to instantiate a `Bridge` object, which represents a physical Hue bridge device
and serves as the central point of communication with the Hue system.
- `Bridge`: Represents a Philips Hue bridge. It provides methods to interact with the bridge, such as authenticating,
sending commands, and querying for connected lights and sensors.
- `EntertainmentConfiguration`: Encapsulates the configuration necessary for setting up entertainment areas,
defining which lights are used, and how they react during an entertainment session.
- `setup_logs`: Simplifies the logging setup process for the entire package, allowing for easy initialization of
logging with customizable settings for file size, backup counts, and log levels.

This module abstracts the complexities involved in directly handling the Hue Entertainment API and provides a
streamlined interface for building applications that can create immersive lighting experiences.
"""

from hue_entertainment_pykit import Discovery, Streaming, create_bridge, setup_logs
from models.bridge import Bridge
from models.entertainment_configuration import EntertainmentConfiguration

__all__ = [
    "Discovery",
    "Streaming",
    "create_bridge",
    "setup_logs",
    "Bridge",
    "EntertainmentConfiguration",
]
