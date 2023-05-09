from repositories.philips_bridge_api import PhilipsBridgeApi


class PhilipsBridgeService:
    """_summary_"""

    def __init__(self, bridge_api: PhilipsBridgeApi) -> None:
        self.__bridge_api = bridge_api

    def print_config(self):
        print(self.__bridge_api.get_config())

    def print_schedules(self):
        print(self.__bridge_api.get_schedules())

    def print_sensors(self):
        print(self.__bridge_api.get_sensors())

    def print_rules(self):
        print(self.__bridge_api.get_rules())
