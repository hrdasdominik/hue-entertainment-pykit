from services.philips_lights_service import PhilipsLightsService


class PhilipsLightsController:
    """_summary_"""

    def __init__(self, lights_service: PhilipsLightsService) -> None:
        self.lights_service = lights_service

    def print_lights_state(self):
        print(self.lights_service.get_lights_state())

    def turn_on_all_lights(self):
        self.lights_service.turn_on_all_lights()

    def turn_off_all_lights(self):
        self.lights_service.turn_off_all_lights()
