from dataclasses import dataclass
from typing import List
from datetime import datetime

from models.philips_base_model import PhilipsBaseModel


@dataclass
class CT:
    min: int
    max: int


@dataclass
class Control:
    mindimlevel: int
    maxlumen: int
    colorgamuttype: str
    colorgamut: List[List[float]]
    ct: CT


@dataclass
class Streaming:
    renderer: bool
    proxy: bool


@dataclass
class Capabilities:
    certified: bool
    control: Control
    streaming: Streaming


@dataclass
class Startup:
    mode: str
    configured: bool


@dataclass
class Config:
    archetype: str
    function: str
    direction: str
    startup: Startup


@dataclass
class State:
    on: bool
    bri: int
    hue: int
    sat: int
    effect: str
    xy: List[float]
    ct: int
    alert: str
    colormode: str
    mode: str
    reachable: bool


@dataclass
class Swupdate:
    state: str
    lastinstall: datetime


@dataclass
class PhilipsLightModel(PhilipsBaseModel):
    id : int
    state: State
    swupdate: Swupdate
    type: str
    name: str
    modelid: str
    manufacturername: str
    productname: str
    capabilities: Capabilities
    config: Config
    uniqueid: str
    swversion: str
    swconfigid: str
    productid: str
