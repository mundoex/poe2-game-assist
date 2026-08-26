import time
from config import ScriptConfig, ScriptConfigData
from screen_types import Size
from pyee import EventEmitter
from EventInfo import EventInfo
from PathOfExile2GameState import PathOfExile2GameState
from PathOfExile2GameStateReader import PathOfExile2GameStateReader

STATE_ATTR_TO_EVENT = {
    "is_health_below_threshold": "on_health_below_threshold",
    "is_mana_below_threshold": "on_mana_below_threshold",
    "is_rage_below_threshold": "on_rage_below_threshold",
    "is_energy_shield_below_threshold": "on_energy_shield_below_threshold",
    "is_poison": "on_poison",
    "is_shocked": "on_shocked",
}

class PathOfExile2GameStateController():
    def __init__(self, config: ScriptConfig, size: Size):
        self.events = EventEmitter()
        self.size = size
        self._last_emitted_at_ms: dict[str, float] = {}
        self.config = config
        self.state = PathOfExile2GameState()
        self.reader = PathOfExile2GameStateReader(size)
        self.reader.configure(config)
        self.frame = 0

    @property
    def _config_data(self) -> ScriptConfigData:
        return self.config.configData

    @property
    def poe2_positions(self):
        return self.reader.positions

    def check_game_state(self) -> None:
        self.frame += 1
        pixel_colors = self.reader.read()
        new_game_state = self.reader.get_game_state_for_pixel_colors(*pixel_colors)
        self.update(new_game_state, pixel_colors)

    def update(self, new_game_state: PathOfExile2GameState, pixel_colors) -> None:
        self.state = new_game_state
        for state_attr, event_name in STATE_ATTR_TO_EVENT.items():
            new_value = getattr(self.state, state_attr)
            if new_value:
                self.emit_if_not_on_cooldown(event_name, new_value, pixel_colors)

        self.emit_if_not_on_cooldown("on_repeat", True, pixel_colors)

    def emit_if_not_on_cooldown(self, event_name: str, value: bool, pixel_colors) -> None:
        action_config = getattr(self._config_data, event_name)
        now_ms = time.monotonic() * 1000
        last_emitted_ms = self._last_emitted_at_ms.get(event_name)

        on_cooldown = last_emitted_ms is not None and (now_ms - last_emitted_ms) < action_config.cooldown_rate_ms
        if not on_cooldown:
            self._last_emitted_at_ms[event_name] = now_ms
            health_pixels_rgb, energy_shield_pixels_rgb, poison_pixel_rgb, mana_pixel_rgb, rage_pixel_rgb = pixel_colors
            self.events.emit(event_name, EventInfo(
                frame=self.frame,
                value=value,
                health_pixels_rgb=health_pixels_rgb,
                energy_shield_pixels_rgb=energy_shield_pixels_rgb,
                poison_pixel_rgb=poison_pixel_rgb,
                mana_pixel_rgb=mana_pixel_rgb,
                rage_pixel_rgb=rage_pixel_rgb,
            ))