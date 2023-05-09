"""_sumarry_"""

from api_v2.light.light_service import LightService


class MenuManager:
    """_sumarry_"""

    def __init__(self, lights_service: LightService) -> None:
        self.__lights_service = lights_service
        self.__is_running = True

    def __print_menu(self) -> None:
        """_sumarry_"""
        print(
            """
              Menu:
                1. Print all lights
                2. Turn on all lights
                3. Turn off all lights
              """
        )

    def __choice(self) -> None:
        """_summary_"""
        user_choice = input("Choice:")
        if user_choice == "1":
            self.__lights_service.print_all_lights()
        elif user_choice == "2":
            self.__lights_service.turn_on_all_lights()
        elif user_choice == "3":
            self.__lights_service.turn_off_all_lights()

    def start(self):
        """_summary_"""
        while self.__is_running:
            self.__print_menu()
            self.__choice()
