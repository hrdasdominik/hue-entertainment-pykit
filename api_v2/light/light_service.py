"""_summary_"""

from typing import List
from api_v2.light.light_model import LightModel
from api_v2.light.light_repository import LightRepository
from utils.logger import logging


class LightService:
    """_summary_"""

    def __init__(self, light_repository: LightRepository):
        self.light_container: List[LightModel] = []
        self.light_repository = light_repository

    def print_all_lights(self) -> None:
        """_summary_"""
        if len(self.light_container) == 0:
            self.get_all_lights()
        for light in self.light_container:
            print(light)

    def check_is_light_container_empty(self) -> bool:
        """_summary_"""
        return self.light_container.count() == 0

    def get_all_lights(self) -> List[LightModel]:
        """_summary_"""
        data = self.light_repository.get_lights()
        lights_data = data.get("data", [])
        for light_data in lights_data:
            light = LightModel(light_data)
            self.light_container.append(light)

        return self.light_container

    def get_light_by_id(self, light_id):
        """_summary_"""
        for light in self.light_container:
            if light.id == light_id:
                return light
        return None

    def turn_on_all_lights(self) -> None:
        """_summary_"""
        if len(self.light_container) == 0:
            self.get_all_lights()
        for light in self.light_container:
            if light.on.on is False:
                light.on.on = True
                data = { "on": light.to_dict()["on"] }
                self.light_repository.change_state(identification=light.id, data=data)
                print(light.id, "changed light state")

    def turn_off_all_lights(self) -> None:
        """_summary_"""
        print("Started all lights turn off command")
        if len(self.light_container) == 0:
            self.get_all_lights()
        for light in self.light_container:
            if light.on.on is True:
                light.on.on = False
                data = { "on": light.to_dict()["on"] }
                self.light_repository.change_state(identification=light.id, data=data)
                logging.info(light.id, "changed light state")
