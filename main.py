"""_summary_"""

from controllers.philips_bridge_controller import PhilipsBridgeController
from controllers.philips_lights_controller import PhilipsLightsController
from services.philips_bridge_service import PhilipsBridgeService
from services.philips_lights_service import PhilipsLightsService
from repositories.philips_bridge_api import PhilipsBridgeApi
from repositories.philips_lights_api import PhilipsLightsApi


def main():
    """_summary_"""
    bridge_api = PhilipsBridgeApi()
    bridge_service = PhilipsBridgeService(bridge_api)
    bridge_controller = PhilipsBridgeController(bridge_service)

    lights_api = PhilipsLightsApi()
    lights_service = PhilipsLightsService(lights_api)
    lights_controller = PhilipsLightsController(lights_service)

    lights_controller.turn_on_all_lights()

if __name__ == "__main__":
    main()
