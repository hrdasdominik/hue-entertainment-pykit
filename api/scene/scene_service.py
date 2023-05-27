"""_summary_"""

from typing import List
from api.scene.scene_model import SceneModel
from api.scene.scene_repository import SceneRepository
from utils.logger import logging


class SceneService:
    """_summary_"""

    def __init__(self, scene_repository: SceneRepository):
        self.scene_container: List[SceneModel] = []
        self.scene_repository = scene_repository

    def print_all_scenes(self) -> None:
        """_summary_"""
        if len(self.scene_container) == 0:
            self.get_all_scenes()
        for scene in self.scene_container:
            print(scene)

    def check_is_scene_container_empty(self) -> bool:
        """_summary_"""
        return self.scene_container.count() == 0

    def get_all_scenes(self) -> List[SceneModel]:
        """_summary_"""
        data = self.scene_repository.get_scenes()
        scenes_data = data.get("data", [])
        for scene_data in scenes_data:
            scene = SceneModel(scene_data)
            self.scene_container.append(scene)

        return self.scene_container

    def get_scene_by_id(self, scene_id: str):
        """_summary_"""
        for scene in self.scene_container:
            if scene.id == scene_id:
                return scene

    def select_scene(self, scene_id: str) -> None:
        """_summary_"""
        for scene in self.scene_container:
            if scene.id == scene_id:
                scene.status.active = 

    def delete_scene(self, scene_id: str) -> None:
        """_summary_"""
        for scene in self.scene_container:
            if scene.id == scene_id:
                data = {"id": scene_id}
                self.scene_repository.delete_scene(data=data)
                return None
