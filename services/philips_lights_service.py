"""_summary_"""

from api_v1.repositories.philips_lights_api import PhilipsLightsApi


class PhilipsLightsService:
    """_summary_"""

    def __init__(self, lights_api: PhilipsLightsApi) -> None:
        self.lights_api = lights_api

    def turn_on_all_lights(self):
        """_summary_"""
        lights = self.lights_api.get_all_lights()
        for light in lights:
            light.state.on = True
            self.lights_api.send_light_data_change(light)

    def turn_off_all_lights(self):
        """_summary_"""
        lights = self.lights_api.get_all_lights()
        for light in lights:
            light.state.on = False
            self.lights_api.send_data_change(light)
