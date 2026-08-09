import threading
from functools import wraps
import keyboard
from config import ScriptConfig, ThresholdActionConfig
from PathOfExile2GameStateController import PathOfExile2GameStateController
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

@only_when_poe2_active
def on_health_below_threshold(is_below: bool):
    print(f"[event] on_health_below_threshold: {is_below}")
    run_threshold_actions(g_config.configData.on_health_below_threshold)

@only_when_poe2_active
def on_mana_below_threshold(is_below: bool):
    print(f"[event] on_mana_below_threshold: {is_below}")
    run_threshold_actions(g_config.configData.on_mana_below_threshold)

@only_when_poe2_active
def on_energy_shield_below_threshold(is_below: bool):
    print(f"[event] on_energy_shield_below_threshold: {is_below}")
    run_threshold_actions(g_config.configData.on_energy_shield_below_threshold)

@only_when_poe2_active
def on_rage_below_threshold(is_below: bool):
    print(f"[event] on_rage_below_threshold: {is_below}")
    run_threshold_actions(g_config.configData.on_rage_below_threshold)

@only_when_poe2_active
def on_poison(is_poison: bool):
    print(f"[event] on_poison: {is_poison}")
    run_threshold_actions(g_config.configData.on_poison)

@only_when_poe2_active
def on_repeat(_: bool):
    print(f"[event] on_repeat")
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
    g_config.save()

    g_size = get_window_geometry()[2:4]

    g_game_controller = PathOfExile2GameStateController(g_config, g_size)
    g_ui = UI(g_config, g_size, g_game_controller, game_logic_fn=run_game_logic)

    g_game_controller.events.on("on_health_below_threshold", on_health_below_threshold)
    g_game_controller.events.on("on_mana_below_threshold", on_mana_below_threshold)
    g_game_controller.events.on("on_energy_shield_below_threshold", on_energy_shield_below_threshold)
    g_game_controller.events.on("on_rage_below_threshold", on_rage_below_threshold)
    g_game_controller.events.on("on_poison", on_poison)
    g_game_controller.events.on("on_repeat", on_repeat)

    threading.Thread(target=g_ui.run_overlay, daemon=True).start()
    g_ui.run_tray()