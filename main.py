import threading
from functools import wraps
import keyboard
from config import ScriptConfig, ThresholdActionConfig
from PathOfExile2GameStateController import PathOfExile2GameStateController
from EventInfo import EventInfo
from ui import UI
from screen_utils import get_window_name, get_window_geometry

g_config: ScriptConfig | None = None
g_is_poe2_open: bool = False
g_game_controller: PathOfExile2GameStateController | None = None
g_ui: UI | None = None

debug_size1 = [1920, 1080]
debug_size2 = [2560, 1440]

THRESHOLD_ACTIONS: dict[str, callable] = {
    "press_health_potion": lambda: keyboard.press_and_release(g_config.configData.health_potion_key),
    "press_mana_potion": lambda: keyboard.press_and_release(g_config.configData.mana_potion_key),
    "press_ability_1": lambda: keyboard.press_and_release(g_config.configData.ability_1_key),
    "press_ability_2": lambda: keyboard.press_and_release(g_config.configData.ability_2_key),
    "press_ability_3": lambda: keyboard.press_and_release(g_config.configData.ability_3_key),
    "press_ability_4": lambda: keyboard.press_and_release(g_config.configData.ability_4_key),
    "press_escape_key": lambda: keyboard.press_and_release("esc"),
}

def run_threshold_actions(action_config: ThresholdActionConfig) -> None:
    """Runs every action whose matching flag is enabled on the given ThresholdActionConfig."""
    for action_name, action_fn in THRESHOLD_ACTIONS.items():
        if getattr(action_config, action_name):
            action_fn()

def only_when_poe2_active(fn):
    """Skips the wrapped handler unless Path of Exile 2 is the active window."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if get_window_name() == "Path of Exile 2":
            return fn(*args, **kwargs)
    return wrapper

def log_event_info(name: str, info: EventInfo) -> None:
    """Pretty-prints an EventInfo, bracketed by separators so consecutive events are easy to tell apart in the console."""
    separator = "-" * 70
    print(separator)
    print(f"| EVENT: {name}  (frame {info.frame})")
    print(f"|   value:                    {info.value}")
    print(f"|   health_pixels_rgb:        {info.health_pixels_rgb}")
    print(f"|   energy_shield_pixels_rgb: {info.energy_shield_pixels_rgb}")
    print(f"|   poison_pixel_rgb:         {info.poison_pixel_rgb}")
    print(f"|   mana_pixel_rgb:           {info.mana_pixel_rgb}")
    print(f"|   rage_pixel_rgb:           {info.rage_pixel_rgb}")
    print(separator)

@only_when_poe2_active
def on_health_below_threshold(info: EventInfo):
    #log_event_info("on_health_below_threshold", info)
    run_threshold_actions(g_config.configData.on_health_below_threshold)

@only_when_poe2_active
def on_mana_below_threshold(info: EventInfo):
    # log_event_info("on_mana_below_threshold", info)
    run_threshold_actions(g_config.configData.on_mana_below_threshold)

@only_when_poe2_active
def on_energy_shield_below_threshold(info: EventInfo):
    # log_event_info("on_energy_shield_below_threshold", info)
    run_threshold_actions(g_config.configData.on_energy_shield_below_threshold)

@only_when_poe2_active
def on_rage_below_threshold(info: EventInfo):
    # log_event_info("on_rage_below_threshold", info)
    run_threshold_actions(g_config.configData.on_rage_below_threshold)

@only_when_poe2_active
def on_poison(info: EventInfo):
    # log_event_info("on_poison", info)
    run_threshold_actions(g_config.configData.on_poison)

@only_when_poe2_active
def on_shocked(info: EventInfo):
    # log_event_info("on_shocked", info)
    run_threshold_actions(g_config.configData.on_shocked)

@only_when_poe2_active
def on_repeat(info: EventInfo):
    # log_event_info("on_repeat", info)
    run_threshold_actions(g_config.configData.on_repeat)

def run_game_logic():
    """Periodically checks/updates game state. Runs until the UI pauses/stops it."""
    if get_window_name() == "Path of Exile 2":
        #TODO find a way to check if player is actually playing (not in menu, not dead, not in cutscene, etc.)
        if g_config.configData.double_check_if_playing: 
            g_game_controller.check_game_state()
        else:
            g_game_controller.check_game_state()

if __name__ == "__main__":
    g_config = ScriptConfig(ScriptConfig.get_default_config_path())
    g_config.load()

    g_size = get_window_geometry()[2:4]

    g_game_controller = PathOfExile2GameStateController(g_config, g_size)
    g_ui = UI(g_config, g_size, g_game_controller, game_logic_fn=run_game_logic)

    g_game_controller.events.on("on_health_below_threshold", on_health_below_threshold)
    g_game_controller.events.on("on_mana_below_threshold", on_mana_below_threshold)
    g_game_controller.events.on("on_energy_shield_below_threshold", on_energy_shield_below_threshold)
    g_game_controller.events.on("on_rage_below_threshold", on_rage_below_threshold)
    g_game_controller.events.on("on_poison", on_poison)
    g_game_controller.events.on("on_shocked", on_shocked)
    g_game_controller.events.on("on_repeat", on_repeat)

    threading.Thread(target=g_ui.run_overlay, daemon=True).start()
    g_ui.run_tray()