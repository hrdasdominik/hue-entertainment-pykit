# Hue Entertainment PyKit
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/hrdasdominik/hue-entertainment-pykit/python-app.yml?branch=main&label=main)
![GitHub Tag](https://img.shields.io/github/v/tag/hrdasdominik/hue-entertainment-pykit?include_prereleases)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fhrdasdominik%2Fhue-entertainment-pykit%2Fmain%2Fpyproject.toml)
![PyPI - Version](https://img.shields.io/pypi/v/hue-entertainment-pykit?link=https%3A%2F%2Fpypi.org%2Fproject%2Fhue-entertainment-pykit%2F)
![PyPI - License](https://img.shields.io/pypi/l/hue-entertainment-pykit?link=https%3A%2F%2Fpypi.org%2Fproject%2Fhue-entertainment-pykit%2F)



<img align="right" alt="HEPK logo" src="docs/logo/horizontal.png" width="400">

## Introduction

Unlock the full spectrum of Philips Hue lighting with the Hue Entertainment PyKit. This Python library simplifies connecting to the Hue Bridge and controlling lights with minimal latency, empowering developers to create dynamic and responsive lighting environments.

---

## Motivation

Confronted with the complexity of the official Hue EDK and challenges in DTLS handshake implementation which many in the community had, Hue Entertainment PyKit was crafted to provide a straightforward, Python-centric approach to light control using the Philips Hue Entertainment API.

---

## Quick Start

### Installing

To install Hue Entertainment PyKit, ensure you have Python installed on your system, and then run the following command:
```sh
pip install hue-entertainment-pykit
```

__Note:__ Python 3.13 and later are currently unsupported due to ___python-mbedtls___ not yet providing compatible 
wheels. This sucks cause last update was in second quarter of 2024 and it looks like there won't be any anymore.

---

## Usage

To interact with your Philips Hue lights you can do:

### Logging Configuration (Optional)

Hue Entertainment PyKit configures logging **only for its own logger namespace**
(`hue_entertainment_pykit.*`). It does not modify the root logger.

```python
import logging
from hue_entertainment_pykit import setup_logs

# Enable library logging with the default formatter and handlers
setup_logs()

# Or customize the logging level (e.g., exclude DEBUG messages)
setup_logs(level=logging.INFO)

# You can also further customize logging by specifying the maximum log file size and the number of backup files
setup_logs(level=logging.INFO, max_file_size=1024 * 1024, backup_count=1)

# Each parameter is optional and comes with predefined default values
```

To log messages from your own application code in the same format, use a
named logger under the same namespace:

```python
import logging

logger = logging.getLogger("hue_entertainment_pykit.example")
logger.info("Example started")
```

If you prefer to use logging.info(...) (root logger), configure it separately:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

#### Silencing noisy third-party logs

Some dependencies (e.g. `urllib3`, `zeroconf`) may emit verbose DEBUG logs if
root logging is enabled. You can reduce noise like this:

```python
import logging

logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("zeroconf").setLevel(logging.WARNING)
```

### Discovery (Optional)

Use only on your Local Area Network (LAN) to discover and fetch all Bridges that can be used then for streaming

```python
from hue_entertainment_pykit import Discovery

discovery = Discovery()

# returns dict[str, Bridge] where the key is name of the bridge and value is the Bridge model with all important info for connecting to Entertainment API
bridges = discovery.discover_bridges()  
```
### Streaming

The Streaming service in Hue Entertainment PyKit provides thread-safe communication with Hue lights, ensuring smooth and uninterrupted interactions. To prevent connection timeouts, the service implements a keep-alive feature: if no command is sent for 9.5 seconds, the last message is automatically resent to maintain the connection.

Below is a streamlined example to set up and manage your streaming session:

```python
import time
from hue_entertainment_pykit import create_bridge, Entertainment, Streaming

# Set up the Bridge instance with the all needed configuration
bridge = create_bridge(
    identification="4abb74df-5b6b-410e-819b-bf4448355dff",
    rid="d476df48-83ad-4430-a104-53c30b46b4d0",
    ip_address="192.168.1.100",
    swversion=1962097030,
    username="8nuTIcK2nOf5oi88-5zPvV1YCt0wTHZIGG8MwXpu",
    hue_app_id="94530efc-933a-4f7c-97e5-ccf1a9fc79af",
    clientkey="B42753E1E1605A1AB90E1B6A0ECF9C51",
    name="1st Bridge"
)

# Set up the Entertainment API service
entertainment_service = Entertainment(bridge)

# Fetch all Entertainment Configurations on the Hue bridge
entertainment_configs = entertainment_service.get_entertainment_configs()

# Add some Entertainment Area selection logic
# For the purposes of example I'm going to do manual selection
entertainment_config = list(entertainment_configs.values())[0]

# Set up the Streaming service
streaming = Streaming(
    bridge, entertainment_config, entertainment_service.get_ent_conf_repo()
)

# Start streaming messages to the bridge
streaming.start_stream()

# Set the color space to xyb or rgb
streaming.set_color_space("xyb")

# Set input commands for the lights
# First three values in the tuple are placeholders for the color RGB8(int) or (in this case) XYB(float) and the last integer is light ID inside the Entertainment API
streaming.set_input((0.0, 0.63435, 0.3, 0))  # Light command for the first light
streaming.set_input((0.63435, 0.0, 0.3, 1))  # Light command for the second light
# ... Add more inputs as needed for additional lights and logic

# For the purpose of example sleep is used for all inputs to process before stop_stream is called
# Inputs are set inside Event queue meaning they're on another thread so user can interact with application continuously
time.sleep(0.1)

# Stop the streaming session
streaming.stop_stream()
```

Replace the placeholders in the `set_input` method with actual light IDs and the color and brightness values you intend to use. The `start_stream` method initiates the streaming session, `set_color_space` configures the color space, and `stop_stream` terminates the session.
