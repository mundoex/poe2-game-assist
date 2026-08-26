from dataclasses import dataclass

@dataclass
class PathOfExile2GameState:
    is_poison: bool = False
    is_health_below_threshold: bool = False
    is_mana_below_threshold: bool = False
    is_rage_below_threshold: bool = False
    is_energy_shield_below_threshold: bool = False
    is_shocked: bool = False
