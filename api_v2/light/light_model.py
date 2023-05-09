"""_summary_"""

from dataclasses import dataclass


@dataclass
class Owner:
    """_summary_"""
    rid: str
    rtype: str


@dataclass
class Metadata:
    """_summary_"""
    name: str
    archetype: str


@dataclass
class On:
    """_summary_"""
    on: str


@dataclass
class Dimming:
    """_summary_"""
    brightness: str
    min_dim_level: str


@dataclass
class ColorTemperature:
    """_summary_"""
    mirek: str
    mirek_valid: str
    mirek_schema: str


@dataclass
class Color:
    """_summary_"""
    xy: str
    gamut: str
    gamut_type: str


@dataclass
class Dynamics:
    """_summary_"""
    status: str
    status_values: str
    speed: str
    speed_valid: str


@dataclass
class Alert:
    """_summary_"""
    action_values: str


@dataclass
class Signaling:
    """_summary_"""
    signal_values: str


@dataclass
class Effects:
    """_summary_"""
    status_values: str
    status: str
    effect_values: str


@dataclass
class Powerup:
    """_summary_"""
    preset: str
    configured: str
    on: str
    dimming: str
    color: str


class LightModel:
    """_summary_"""
    def __init__(self, data):
        self.id = data['id']
        self.id_v1 = data['id_v1']
        self.owner = Owner(**data['owner'])
        self.metadata = Metadata(**data['metadata'])
        self.on = On(**data['on'])
        self.dimming = Dimming(**data['dimming'])
        self.dimming_delta = data['dimming_delta']
        self.color_temperature = ColorTemperature(**data['color_temperature'])
        self.color_temperature_delta = data['color_temperature_delta']
        self.color = Color(**data['color'])
        self.dynamics = Dynamics(**data['dynamics'])
        self.alert = Alert(**data['alert'])
        self.signaling = Signaling(**data['signaling'])
        self.mode = data['mode']
        self.effects = Effects(**data['effects'])
        self.powerup = Powerup(**data['powerup'])
        self.type = data['type']


    def __str__(self) -> str:
        return (
            f"Light ID: {self.id}\nName: {self.metadata.name}\n"
            + f"On: {self.on.on}\nBrightness: {self.dimming.brightness}\n"
        )

    def to_dict(self) -> dict:
        """_summary_"""
        return {
            'id': self.id,
            'id_v1': self.id_v1,
            'owner': self.owner.__dict__,
            'metadata': self.metadata.__dict__,
            'on': self.on.__dict__,
            'dimming': self.dimming.__dict__,
            'dimming_delta': self.dimming_delta,
            'color_temperature': self.color_temperature.__dict__,
            'color_temperature_delta': self.color_temperature_delta,
            'color': self.color.__dict__,
            'dynamics': self.dynamics.__dict__,
            'alert': self.alert.__dict__,
            'signaling': self.signaling.__dict__,
            'mode': self.mode,
            'effects': self.effects.__dict__,
            'powerup': self.powerup.__dict__,
            'type': self.type
        }
