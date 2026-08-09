import json
import os
import sys
from dataclasses import asdict, dataclass, field, fields, is_dataclass

def get_default_config_path_windows() -> str:
    base_dir = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "config.json")

def get_default_config_path_linux() -> str:
    raise NotImplementedError("Default config path for Linux is not implemented. Please specify the config path manually.")

@dataclass
class ThresholdActionConfig:
    press_health_potion: bool = False
    press_mana_potion: bool = False
    press_ability_1: bool = False
    press_ability_2: bool = False
    press_ability_3: bool = False
    press_ability_4: bool = False
    press_escape_key: bool = False
    cooldown_rate_ms: int = 10000

@dataclass
class ScriptConfigData:
    check_screen_rate_ms: int = 500
    double_check_if_playing: bool = False

    hp_threshold_percent: int = 50
    mana_threshold_percent: int = 50
    rage_threshold_percent: int = 0
    energy_shield_below_bars: int = 1
    energy_shield_percent: int = 0
    chaos_inoculation: bool = False
    health_reservation_percent: int = 0
    has_runic_ward: bool = False

    health_potion_key: str = "1"
    mana_potion_key: str = "2"
    ability_1_key: str = "Q"
    ability_2_key: str = "W"
    ability_3_key: str = "E"
    ability_4_key: str = "R"

    hotkey_toggle: str = "F7"
    hotkey_exit: str = "F8"

    on_health_below_threshold: ThresholdActionConfig = field(default_factory=ThresholdActionConfig)
    on_mana_below_threshold: ThresholdActionConfig = field(default_factory=ThresholdActionConfig)
    on_rage_below_threshold: ThresholdActionConfig = field(default_factory=ThresholdActionConfig)
    on_energy_shield_below_threshold: ThresholdActionConfig = field(default_factory=ThresholdActionConfig)
    on_poison: ThresholdActionConfig = field(default_factory=ThresholdActionConfig)
    on_repeat: ThresholdActionConfig = field(default_factory=ThresholdActionConfig)

    debug: bool = False

def _apply_config_data(instance, data: dict) -> None:
    for f in fields(instance):
        if f.name not in data:
            continue

        value = data[f.name]
        if is_dataclass(f.type) and isinstance(value, dict):
            _apply_config_data(getattr(instance, f.name), value)
        elif isinstance(value, f.type):
            setattr(instance, f.name, value)

class ScriptConfig:
    def __init__(self, path: str):
        self.path = path
        self.configData = None

    @staticmethod
    def get_default_config_path() -> str:
        if os.name == "nt":
            return get_default_config_path_windows()
        else:
            return get_default_config_path_linux()

    def load(self) -> None:
        self.configData = ScriptConfigData()

        with open(self.path) as f:
            data = json.load(f)

        _apply_config_data(self.configData, data)

    def write_text(self, text: str) -> None:
        with open(self.path, "w") as f:
            f.write(text)

    def to_text(self) -> str:
        if self.configData is None:
            self.configData = ScriptConfigData()

        return json.dumps(asdict(self.configData), indent=2)

    def save(self) -> None:
        self.write_text(self.to_text())