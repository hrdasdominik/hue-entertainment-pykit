"""_summary_"""

import uuid
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass
class Target:
    """_summary_"""

    rid: uuid.UUID
    rtype: str


@dataclass
class Action:
    """_summary_"""

    on: Dict[str, Any]
    dimming: Dict[str, Any]
    color_temperature: Dict[str, Any]


@dataclass
class ActionItem:
    """_summary_"""

    target: Target
    action: Action


@dataclass
class Image:
    """_summary_"""

    rid: uuid.UUID
    rtype: str


@dataclass
class Metadata:
    """_summary_"""

    name: str
    image: Image


@dataclass
class Group:
    """_summary_"""

    rid: uuid.UUID
    rtype: str


@dataclass
class PaletteItem:
    """_summary_"""

    color_temperature: Dict[str, Any]
    dimming: Dict[str, Any]


@dataclass
class Palette:
    """_summary_"""

    color: List[Dict[str, Any]]
    dimming: List[Dict[str, Any]]
    color_temperature: List[PaletteItem]
    effects: List[Dict[str, Any]]


@dataclass
class Status:
    """_summary_"""

    active: str


class SceneModel:
    """_summary_"""

    def __init__(self, data: Dict[str, Any]):
        self.id = uuid.UUID(data["id"])
        self.id_v1 = data["id_v1"]
        self.actions = [ActionItem(**action) for action in data["actions"]]
        self.recall = data["recall"]
        self.metadata = Metadata(**data["metadata"])
        self.group = Group(**data["group"])
        self.palette = Palette(**data["palette"])
        self.speed = data["speed"]
        self.auto_dynamic = data["auto_dynamic"]
        self.status = Status(**data["status"])
        self.type = data["type"]
    
    def __str__(self) -> str:
        return (
            f"Name: {self.metadata.name}\n"
            + f"Active: {self.status.active}\n"
            + f"Color: {self.palette.color}\n" 
        )
