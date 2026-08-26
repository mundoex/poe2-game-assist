from dataclasses import dataclass
from screen_types import RGB

@dataclass
class EventInfo:
    """Debug info passed to event handlers instead of the raw triggering value."""
    frame: int
    value: bool
    health_pixels_rgb: list[RGB]
    energy_shield_pixels_rgb: list[RGB]
    poison_pixel_rgb: RGB
    mana_pixel_rgb: RGB
    rage_pixel_rgb: RGB
