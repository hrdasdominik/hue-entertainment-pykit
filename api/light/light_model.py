"""_summary_"""

from dataclasses import dataclass


@dataclass
class Owner:
    """_summary_"""
    rid: str
    rtype: str

    def __eq__(self, other):
        if not isinstance(other, Owner):
            return False
        return (self.rid == other.rid and
                self.rtype == other.rtype)


@dataclass
class Metadata:
    """_summary_"""
    name: str
    archetype: str

    def __eq__(self, other):
        if not isinstance(other, Metadata):
            return False
        return (self.name == other.name and
                self.archetype == other.archetype)


@dataclass
class On:
    """_summary_"""
    on: bool

    def __eq__(self, other):
        if not isinstance(other, On):
            return False
        return self.on == other.on


@dataclass
class Dimming:
    """_summary_"""
    brightness: str
    min_dim_level: str

    def __eq__(self, other):
        if not isinstance(other, Dimming):
            return False
        return (self.brightness == other.brightness and
                self.min_dim_level == other.min_dim_level)


@dataclass
class ColorTemperature:
    """_summary_"""
    mirek: str
    mirek_valid: str
    mirek_schema: str

    def __eq__(self, other):
        if not isinstance(other, ColorTemperature):
            return False
        return (self.mirek == other.mirek and
                self.mirek_valid == other.mirek_valid and
                self.mirek_schema == other.mirek_schema)


@dataclass
class Color:
    """_summary_"""
    xy: str
    gamut: str
    gamut_type: str

    def __eq__(self, other):
        if not isinstance(other, Color):
            return False
        return (self.xy == other.xy and
                self.gamut == other.gamut and
                self.gamut_type == other.gamut_type)


@dataclass
class Dynamics:
    """_summary_"""
    status: str
    status_values: str
    speed: str
    speed_valid: str

    def __eq__(self, other):
        if not isinstance(other, Dynamics):
            return False
        return (self.status == other.status and
                self.status_values == other.status_values and
                self.speed == other.speed and
                self.speed_valid == other.speed_valid)


@dataclass
class Alert:
    """_summary_"""
    action_values: str

    def __eq__(self, other):
        if not isinstance(other, Alert):
            return False
        return self.action_values == other.action_values


@dataclass
class Signaling:
    """_summary_"""
    signal_values: str

    def __eq__(self, other):
        if not isinstance(other, Signaling):
            return False
        return self.signal_values == other.signal_values


@dataclass
class Effects:
    """_summary_"""
    status_values: str
    status: str
    effect_values: str

    def __eq__(self, other):
        if not isinstance(other, Effects):
            return False
        return (self.status_values == other.status_values and
                self.status == other.status and
                self.effect_values == other.effect_values)


@dataclass
class Powerup:
    """_summary_"""
    preset: str
    configured: str
    on: str
    dimming: str
    color: str

    def __eq__(self, other):
        if not isinstance(other, Powerup):
            return False
        return (self.preset == other.preset and
                self.configured == other.configured and
                self.on == other.on and
                self.dimming == other.dimming and
                self.color == other.color)


class Light:
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

    def __eq__(self, other):
        if not isinstance(other, Light):
            return False
        return (self.id == other.id and
                self.id_v1 == other.id_v1 and
                self.owner == other.owner and
                self.metadata == other.metadata and
                self.on == other.on and
                self.dimming == other.dimming and
                self.dimming_delta == other.dimming_delta and
                self.color_temperature == other.color_temperature and
                self.color_temperature_delta == other.color_temperature_delta and
                self.color == other.color and
                self.dynamics == other.dynamics and
                self.alert == other.alert and
                self.signaling == other.signaling and
                self.mode == other.mode and
                self.effects == other.effects and
                self.powerup == other.powerup and
                self.type == other.type)

    def to_dict(self) -> dict:
        """_summary_"""
        return {
            'id': self.id,
            'id_v1': self.id_v1,
            'owner': self.owner.__dict__,
            'metadata': self.metadata.__dict__,
            'on': self.on.__dict__ if isinstance(self.on, On) else self.on,
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
