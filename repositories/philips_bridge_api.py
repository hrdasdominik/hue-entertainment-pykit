from repositories.philips_base_api import PhilipsBaseApi


class PhilipsBridgeApi(PhilipsBaseApi):
    """_summary_"""

    def __init__(self) -> None:
        super().__init__()
        self.__endpoint_config = "/config"
        self.__endpoint_schedules = "/schedules"
        self.__endpoint_sensors = "/sensors"
        self.__endpoint_rules = "/rules"

    def get_config(self):
        return self.get_data(self.__endpoint_config)

    def get_schedules(self):
        return self.get_data(self.__endpoint_schedules)

    def get_sensors(self):
        return self.get_data(self.__endpoint_sensors)

    def get_rules(self):
        return self.get_data(self.__endpoint_rules)
