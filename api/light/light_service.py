"""_summary_"""

from typing import List
from api.light.light_model import LightModel
from api.light.light_repository import LightRepository
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

    def turn_on_light(self) -> None:
        """_summary_"""
        logging.info("Started light turn on command")
        if len(self.light_container) == 0:
            self.get_all_lights()

        self.print_all_lights()
        user_input = int(input("Choice: "))
        if len(self.light_container) > (user_input - 1):
            light: LightModel = self.light_container[user_input - 1]
            if light.on.on is False:
                light.on.on = True
            else:
                logging.error(f"Light '{light.metadata.name}' state is already ON")
                return None

            data = {"on": light.to_dict()["on"]}
            self.light_repository.put_light(identification=light.id, data=data)
            logging.info(f"'{light.metadata.name}' changed light state")
        else:
            logging.error("Selected value is out of bounds")

    def turn_off_light(self) -> None:
        """_summary_"""
        logging.info("Started light turn off command")
        if len(self.light_container) == 0:
            self.get_all_lights()

        self.print_all_lights()
        user_input = int(input("Choice: "))
        if len(self.light_container) > (user_input - 1):
            light: LightModel = self.light_container[user_input - 1]
            if light.on.on is True:
                light.on.on = False
            else:
                logging.error(f"Light '{light.metadata.name}' state is already OFF")
                return None

            data = {"on": light.to_dict()["on"]}
            self.light_repository.put_light(identification=light.id, data=data)
            logging.info(f"'{light.metadata.name}' changed light state")
        else:
            logging.error("Selected value is out of bounds")
