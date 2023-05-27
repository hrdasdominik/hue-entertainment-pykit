"""_summary_"""

from services.philips_lights_service import PhilipsLightsService


class PhilipsLightsController:
    """_summary_"""

    def __init__(self, lights_service: PhilipsLightsService) -> None:
        self.__lights_service = lights_service

    def print_all_lights(self):
        """_summary_"""
        print(self.__lights_service.lights_api.get_all_lights())

    def print_lights_state(self):
        """_summary_"""
        print(self.__lights_service.lights_api.get_light_state())

    def turn_on_all_lights(self):
        """_summary_"""
        self.__lights_service.turn_on_all_lights()

    def turn_off_all_lights(self):
        """_summary_"""
        self.__lights_service.turn_off_all_lights()
