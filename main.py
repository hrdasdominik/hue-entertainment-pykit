"""_summary_"""

from api.light.light_repository import LightRepository
from api.light.light_service import LightService

from api.scene.scene_repository import SceneRepository
from api.scene.scene_service import SceneService

from menu_manager import MenuManager


def main():
    """_summary_"""
    light_repository = LightRepository()
    light_service = LightService(light_repository)
    
    scene_repository = SceneRepository()
    scene_service = SceneService(scene_repository)

    menu_manager = MenuManager(light_service, scene_service)
    menu_manager.start()


if __name__ == "__main__":
    main()
