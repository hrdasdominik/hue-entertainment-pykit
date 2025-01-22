"""
This module provides a comprehensive representation of a Philips Hue `Light` resource model,
closely mirroring the JSON structure and style found in the Philips Hue API.

The `Light` class encapsulates all aspects of a Philips Hue light resource, adhering
to the Philips Hue API specifications. It includes robust validation and detailed attributes
necessary for effective resource management. Supporting dataclasses such as `Owner`, `Metadata`,
`Dimming`, `ColorTemperature`, `Color`, `Dynamics`, and others ensure modularity and clarity.

Classes:
- Owner: Represents the owner of a resource.
- Metadata: Represents metadata for a light.
- ProductData: Represents extra product-related data (optional extension).
- Identify: Represents an identify action placeholder (often empty).
- On: Represents the ON/OFF state of the light.
- Dimming: Represents dimming settings for a light.
- ColorTemperature: Represents color temperature settings for a light.
- Color: Represents color settings (including gamut) for a light.
- Dynamics: Represents dynamic effects settings for a light.
- Alert: Represents alert (breathe) settings for a light.
- Signaling: Represents advanced signaling instructions for a light.
- Effects: Represents various effect states for a light.
- EffectsV2: Represents extended effect states for a light (v2 features).
- TimedEffects: Represents timed effects (e.g., sunrise, sunset).
- Powerup: Represents power-on behavior configuration.
- Light: Represents the complete configuration of a Philips Hue Light.

Example Usage:
```python
# Example usage to instantiate this Light model manually:
light_example = Light(
    id="134bef36-714a-4321-a252-b473d44e4b1d",
    id_v1="/lights/3",
    owner=Owner(
        rid="aa3ec741-25e4-4af6-a703-d63c1b1841af",
        rtype="device"
    ),
    metadata=Metadata(
        name="Lamp on left side bed",
        archetype="table_shade"
    ),
    product_data=ProductData(
        function="mixed"
    ),
    identify=Identify(),
    service_id=0,
    on=On(on=True),
    dimming=Dimming(
        brightness=49.8,
        min_dim_level=0.2
    ),
    color_temperature=ColorTemperature(
        mirek=493,
        mirek_valid=True,
        mirek_schema=MirekSchema(
            mirek_minimum=153,
            mirek_maximum=500
        )
    ),
    color=Color(
        xy=ColorCoordinates(x=0.5236, y=0.4137),
        gamut=Gamut(
            red=ColorCoordinates(x=0.6915, y=0.3083),
            green=ColorCoordinates(x=0.17, y=0.7),
            blue=ColorCoordinates(x=0.1532, y=0.0475)
        ),
        gamut_type="C"
    ),
    dynamics=Dynamics(
        status="none",
        speed=0.0,
        speed_valid=False,
        status_values=["none", "dynamic_palette"]
    ),
    alert=Alert(
        action_values=["breathe"]
    ),
    signaling=Signaling(
        signal_values=["no_signal", "on_off", "on_off_color", "alternating"]
    ),
    mode="normal",
    effects=Effects(
        status_values=[
            "no_effect", "candle", "fire", "prism", "sparkle", "opal",
            "glisten", "underwater", "cosmos", "sunbeam", "enchant"
        ],
        status="no_effect",
        effect_values=[
            "no_effect", "candle", "fire", "prism", "sparkle", "opal",
            "glisten", "underwater", "cosmos", "sunbeam", "enchant"
        ]
    ),
    effects_v2=EffectsV2(
        action=EffectsV2Action(
            effect_values=[
                "no_effect", "candle", "fire", "prism", "sparkle", "opal",
                "glisten", "underwater", "cosmos", "sunbeam", "enchant"
            ]
        ),
        status=EffectsV2Status(
            effect="no_effect",
            effect_values=[
                "no_effect", "candle", "fire", "prism", "sparkle", "opal",
                "glisten", "underwater", "cosmos", "sunbeam", "enchant"
            ]
        )
    ),
    timed_effects=TimedEffects(
        status_values=["no_effect", "sunrise", "sunset"],
        status="no_effect",
        effect_values=["no_effect", "sunrise", "sunset"]
    ),
    powerup=Powerup(
        preset="last_on_state",
        configured=True,
        on=PowerupOn(
            mode="on",
            on=On(on=True)
        ),
        dimming=PowerupDimming(mode="previous"),
        color=PowerupColor(mode="previous")
    )
)
"""

import re
from dataclasses import dataclass, field
from typing import Optional

@dataclass
class Owner:
    """
    Represents the owner of a resource (e.g., a device).

    Attributes:
        rid (str): UUID of the owner resource.
        rtype (str): Type of the owner resource (e.g., 'device').
    """

    rid: str
    rtype: str

    def __post_init__(self):
        # Validate that rid is a well-formed UUID.
        if not re.match(r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$", self.rid, re.IGNORECASE):
            raise ValueError(f"Owner.rid must be a valid UUID: {self.rid}")

        # Basic validation for rtype (expand as needed).
        valid_rtypes = {"device", "bridge_home", "room", "zone", "service", "light", "button"}
        if self.rtype not in valid_rtypes:
            raise ValueError(f"Owner.rtype must be one of {valid_rtypes}, got '{self.rtype}'")


@dataclass
class Metadata:
    """
    Represents metadata about a light.

    Attributes:
        name (str): Name of the light. [1..32 characters].
        archetype (str): Archetype (shape/purpose) of the light.
    """

    name: str
    archetype: str

    def __post_init__(self):
        # Validate name length is between 1 and 32.
        if not (1 <= len(self.name) <= 32):
            raise ValueError(f"Metadata.name must be 1..32 characters, got {len(self.name)}.")

        # Example set of valid archetypes, shorten or expand as necessary.
        valid_archetypes = {
            "unknown_archetype", "classic_bulb", "table_shade", "pendant_round",
            "floor_lantern", "ceiling_round", "candle_bulb"
        }
        if self.archetype not in valid_archetypes:
            raise ValueError(f"Metadata.archetype must be one of {valid_archetypes}, got '{self.archetype}'")


@dataclass
class ProductData:
    """
    Represents extra product-related data.

    Attributes:
        function (str): Light function (e.g., 'mixed').
    """

    function: str

    def __post_init__(self):
        # Just a quick demonstration check:
        valid_functions = {"mixed", "functional", "decorative"}
        if self.function not in valid_functions:
            raise ValueError(f"ProductData.function must be one of {valid_functions}, got '{self.function}'")


@dataclass
class Identify:
    """
    Represents an identify action placeholder (often empty).
    Typically used for triggering a flash/breathe behavior on the actual device.
    """
    # No fields, so no validations in `__post_init__`.
    pass


@dataclass
class On:
    """
    Represents the ON/OFF state of a light.

    Attributes:
        on (bool): True if the light is ON, False otherwise.
    """

    on: bool

    def __post_init__(self):
        if not isinstance(self.on, bool):
            raise ValueError(f"On.on must be a boolean, got {type(self.on).__name__}")


@dataclass
class Dimming:
    """
    Represents dimming configuration for a light.

    Attributes:
        brightness (float): Brightness level [0.0 .. 100.0].
        min_dim_level (float): Minimum dim level the device can handle.
    """

    brightness: float
    min_dim_level: float = 0.0

    def __post_init__(self):
        if not (0.0 < self.brightness <= 100.0):
            raise ValueError(
                f"Dimming.brightness must be in the range (0.0..100.0], got {self.brightness}"
            )
        if not (0.0 <= self.min_dim_level < self.brightness):
            # Typically the min_dim_level is smaller than the actual brightness setting
            # or at least non-negative. Feel free to adjust logic.
            raise ValueError(
                f"Dimming.min_dim_level must be >= 0.0 and less than brightness. Got {self.min_dim_level}"
            )


@dataclass
class MirekSchema:
    """
    Represents the valid range for mirek (color temperature).

    Attributes:
        mirek_minimum (int): Minimum valid mirek value.
        mirek_maximum (int): Maximum valid mirek value.
    """

    mirek_minimum: int
    mirek_maximum: int

    def __post_init__(self):
        # Hue standard: 153..500
        if self.mirek_minimum < 153 or self.mirek_maximum > 500:
            raise ValueError(
                f"MirekSchema range must be within 153..500, got {self.mirek_minimum}-{self.mirek_maximum}"
            )
        if self.mirek_minimum > self.mirek_maximum:
            raise ValueError(
                "MirekSchema.mirek_minimum must be <= mirek_maximum"
            )


@dataclass
class ColorTemperature:
    """
    Represents color temperature settings for a light.

    Attributes:
        mirek (int): Current mirek value (153..500).
        mirek_valid (bool): Whether current mirek is valid for the light.
        mirek_schema (Optional[MirekSchema]): The valid range for mirek values.
    """

    mirek: int
    mirek_valid: bool
    mirek_schema: Optional[MirekSchema] = None

    def __post_init__(self):
        if not (153 <= self.mirek <= 500):
            raise ValueError(f"ColorTemperature.mirek must be 153..500, got {self.mirek}")
        if not isinstance(self.mirek_valid, bool):
            raise ValueError(f"ColorTemperature.mirek_valid must be a bool, got {type(self.mirek_valid).__name__}")


@dataclass
class ColorCoordinates:
    """
    Represents x/y coordinates in a color gamut.

    Attributes:
        x (float): X coordinate [0.0 .. 1.0].
        y (float): Y coordinate [0.0 .. 1.0].
    """

    x: float
    y: float

    def __post_init__(self):
        if not (0.0 <= self.x <= 1.0):
            raise ValueError(f"ColorCoordinates.x must be 0.0..1.0, got {self.x}")
        if not (0.0 <= self.y <= 1.0):
            raise ValueError(f"ColorCoordinates.y must be 0.0..1.0, got {self.y}")


@dataclass
class Gamut:
    """
    Represents the color gamut boundaries.

    Attributes:
        red (ColorCoordinates): Gamut boundary for red.
        green (ColorCoordinates): Gamut boundary for green.
        blue (ColorCoordinates): Gamut boundary for blue.
    """

    red: ColorCoordinates
    green: ColorCoordinates
    blue: ColorCoordinates

@dataclass
class Color:
    """
    Represents color configuration for a light.

    Attributes:
        xy (ColorCoordinates): Current color coordinates.
        gamut (Optional[Gamut]): Color gamut definition.
        gamut_type (Optional[str]): The type of the color gamut (e.g., 'A', 'B', 'C').
    """

    xy: ColorCoordinates
    gamut: Optional[Gamut] = None
    gamut_type: Optional[str] = None

    def __post_init__(self):
        # If a gamut is provided, you might want to ensure the xy lies within that gamut, etc.
        # For demonstration, no further checks here unless needed.
        pass


@dataclass
class Dynamics:
    """
    Represents dynamic effects settings for a light.

    Attributes:
        status (str): Current dynamic effect status (e.g., 'none', 'dynamic_palette').
        speed (float): Speed of the dynamic effect [0.0..1.0].
        speed_valid (bool): Whether the speed is valid for this light.
        status_values (list[str]): Possible statuses.
    """

    status: str
    speed: float
    speed_valid: bool
    status_values: list[str] = field(default_factory=list)

    def __post_init__(self):
        if not (0.0 <= self.speed <= 1.0):
            raise ValueError(f"Dynamics.speed must be 0.0..1.0, got {self.speed}")
        if not isinstance(self.speed_valid, bool):
            raise ValueError("Dynamics.speed_valid must be bool")
        if self.status_values and self.status not in self.status_values:
            raise ValueError(
                f"Dynamics.status '{self.status}' not in allowed values {self.status_values}"
            )


@dataclass
class Alert:
    """
    Represents alert/breathe actions for a light.

    Attributes:
        action_values (list[str]): Possible alert actions (e.g., ['breathe']).
    """

    action_values: list[str] = field(default_factory=list)

    def __post_init__(self):
        # If your design demands that 'breathe' is in action_values, you can add checks here.
        pass


@dataclass
class Signaling:
    """
    Represents advanced signaling states for a light.

    Attributes:
        signal_values (list[str]): Possible signal states.
    """

    signal_values: list[str] = field(default_factory=list)


@dataclass
class Effects:
    """
    Represents various effect states for a light.

    Attributes:
        status_values (list[str]): Possible statuses.
        status (str): Current status (e.g., 'no_effect').
        effect_values (list[str]): Possible effect values.
    """

    status_values: list[str] = field(default_factory=list)
    status: str = "no_effect"
    effect_values: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.status_values and self.status not in self.status_values:
            raise ValueError(f"Effects.status '{self.status}' not in {self.status_values}")


@dataclass
class EffectsV2Action:
    """
    Represents 'action' part of the V2 effects structure.

    Attributes:
        effect_values (list[str]): Allowed effect values.
    """

    effect_values: list[str] = field(default_factory=list)


@dataclass
class EffectsV2Status:
    """
    Represents 'status' part of the V2 effects structure.

    Attributes:
        effect (str): Current effect (e.g. 'no_effect').
        effect_values (list[str]): Possible effect values.
    """

    effect: str = "no_effect"
    effect_values: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.effect_values and self.effect not in self.effect_values:
            raise ValueError(
                f"EffectsV2Status.effect '{self.effect}' not in {self.effect_values}"
            )


@dataclass
class EffectsV2:
    """
    Represents extended effect states for a light.

    Attributes:
        action (EffectsV2Action): Action sub-structure.
        status (EffectsV2Status): Status sub-structure.
    """

    action: EffectsV2Action
    status: EffectsV2Status


@dataclass
class TimedEffects:
    """
    Represents timed effects (sunrise, sunset, etc.) for a light.

    Attributes:
        status_values (list[str]): Possible timed statuses.
        status (str): Current timed effect status (e.g. 'no_effect').
        effect_values (list[str]): Possible timed effect values.
    """

    status_values: list[str] = field(default_factory=list)
    status: str = "no_effect"
    effect_values: list[str] = field(default_factory=list)

    def __post_init__(self):
        if self.status_values and self.status not in self.status_values:
            raise ValueError(f"TimedEffects.status '{self.status}' not in {self.status_values}")


@dataclass
class PowerupOn:
    """
    Represents the 'on' structure inside the powerup object.

    Attributes:
        mode (str): 'on' | 'previous' | 'off'.
        on (Optional[On]): Nested On object if mode is 'on'.
    """

    mode: str
    on: Optional[On] = None

    def __post_init__(self):
        valid_modes = {"on", "previous", "off"}
        if self.mode not in valid_modes:
            raise ValueError(f"PowerupOn.mode must be in {valid_modes}, got '{self.mode}'")
        if self.mode == "on" and self.on is None:
            raise ValueError("PowerupOn.on must be provided if mode='on'")


@dataclass
class PowerupDimming:
    """
    Represents the 'dimming' part of the powerup configuration.

    Attributes:
        mode (str): e.g. 'previous'
    """

    mode: str

    def __post_init__(self):
        valid_modes = {"previous", "custom"}
        if self.mode not in valid_modes:
            # Adjust as needed; if 'custom', you'd define a custom level, etc.
            raise ValueError(f"PowerupDimming.mode must be in {valid_modes}, got '{self.mode}'")


@dataclass
class PowerupColor:
    """
    Represents the 'color' part of the powerup configuration.

    Attributes:
        mode (str): e.g. 'previous'
    """

    mode: str

    def __post_init__(self):
        valid_modes = {"previous", "custom"}
        if self.mode not in valid_modes:
            raise ValueError(f"PowerupColor.mode must be in {valid_modes}, got '{self.mode}'")

@dataclass
class Powerup:
    """
    Represents power-up behavior configuration for a light.

    Attributes:
        preset (str): e.g. 'last_on_state'
        configured (bool): Whether powerup is configured.
        on (PowerupOn): On-state behavior upon power restore.
        dimming (PowerupDimming): Dimming behavior upon power restore.
        color (PowerupColor): Color behavior upon power restore.
    """

    preset: str
    configured: bool
    on: PowerupOn
    dimming: PowerupDimming
    color: PowerupColor

    def __post_init__(self):
        valid_presets = {"last_on_state", "powerfail", "custom"}
        if self.preset not in valid_presets:
            raise ValueError(f"Powerup.preset must be in {valid_presets}, got '{self.preset}'")


@dataclass
class Light:
    """
    Represents a complete Philips Hue Light resource.

    Attributes:
        type (str): Resource type (always "light").
        id (str): UUID of the light.
        id_v1 (Optional[str]): Legacy v1 path-like identifier (e.g. "/lights/3").
        owner (Owner): The owner (e.g. the device).
        metadata (Metadata): Metadata about the light.
        product_data (Optional[ProductData]): Extended product-related data.
        identify (Optional[Identify]): Identify action structure.
        service_id (int): Internal service ID (>= 0).
        on (On): ON/OFF state.
        dimming (Optional[Dimming]): Dimming settings.
        color_temperature (Optional[ColorTemperature]): Color temperature settings.
        color (Optional[Color]): Full color configuration.
        dynamics (Optional[Dynamics]): Dynamic effects settings.
        alert (Optional[Alert]): Alert/breathe configuration.
        signaling (Optional[Signaling]): Advanced signaling configuration.
        mode (Optional[str]): Light mode (e.g., "normal").
        effects (Optional[Effects]): Basic effect states.
        effects_v2 (Optional[EffectsV2]): Extended effect states (v2).
        timed_effects (Optional[TimedEffects]): Timed effect states.
        powerup (Optional[Powerup]): Power-up behavior configuration.
    """

    type: str = field(default="light", init=False)
    id: str = field(default="")
    id_v1: Optional[str] = None
    owner: Owner = field(default=None)
    metadata: Metadata = field(default=None)
    product_data: Optional[ProductData] = None
    identify: Optional[Identify] = None
    service_id: int = 0
    on: On = field(default=None)
    dimming: Optional[Dimming] = None
    color_temperature: Optional[ColorTemperature] = None
    color: Optional[Color] = None
    dynamics: Optional[Dynamics] = None
    alert: Optional[Alert] = None
    signaling: Optional[Signaling] = None
    mode: Optional[str] = None
    effects: Optional[Effects] = None
    effects_v2: Optional[EffectsV2] = None
    timed_effects: Optional[TimedEffects] = None
    powerup: Optional[Powerup] = None

    def __post_init__(self):
        uuid_regex = r"^[0-9a-f]{8}-([0-9a-f]{4}-){3}[0-9a-f]{12}$"
        if not re.match(uuid_regex, self.id, re.IGNORECASE):
            raise ValueError(f"Light.id must be a valid UUID, got '{self.id}'")

        if self.id_v1 and not self.id_v1.startswith("/lights/"):
            raise ValueError("Light.id_v1 must start with '/lights/' if provided.")

        if self.service_id < 0:
            raise ValueError(f"Light.service_id must be >= 0, got {self.service_id}")

        if self.owner is None:
            raise ValueError("Light.owner is required and cannot be None.")

        if self.metadata is None:
            raise ValueError("Light.metadata is required and cannot be None.")

        if self.on is None:
            raise ValueError("Light.on is required and cannot be None.")

        valid_modes = {"normal", "streaming"}
        if self.mode and self.mode not in valid_modes:
            raise ValueError(f"Light.mode must be one of {valid_modes}, got '{self.mode}'")