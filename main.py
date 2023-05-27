"""_summary_"""

from api_v2.light.light_repository import LightRepository
from api_v2.light.light_service import LightService

from menu_manager import MenuManager


def main():
    """_summary_"""
    light_repository = LightRepository()
    light_service = LightService(light_repository)

    menu_manager = MenuManager(light_service)
    menu_manager.start()


if __name__ == "__main__":
    main()
