"""_sumarry_"""

from api.light.light_service import LightService
from api.scene.scene_service import SceneService


class MenuManager:
    """_sumarry_"""

    def __init__(self, lights_service: LightService, scene_service: SceneService) -> None:
        self.__lights_service = lights_service
        self.__scene_service = scene_service
        self.__is_running = True

    def __print_menu(self) -> None:
        """_sumarry_"""
        print(
            """
              Menu:
                1. Print all lights
                2. Turn on a light
                3. Turn off a light
                4. Print all scenes
                5. Select scene
              """
        )

    def __choice(self) -> None:
        """_summary_"""
        user_choice = input("Choice:")
        
        if user_choice == "1":
            self.__lights_service.print_all_lights()
        elif user_choice == "2":
            self.__lights_service.turn_on_light()
        elif user_choice == "3":
            self.__lights_service.turn_off_light()
        elif user_choice == "4":
            self.__scene_service.print_all_scenes()
        elif user_choice == "5":
            pass

    def start(self):
        """_summary_"""
        while self.__is_running:
            self.__print_menu()
            self.__choice()
