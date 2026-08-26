from functools import cached_property
from screen_types import RGB, Size
from screen_utils import get_pixels
from IConfigurable import IConfigurable
from config import ScriptConfig
from color_math import is_pink_color, is_red_color, is_green_color, is_blue_color, is_white_color, is_purple_color, is_near_black
from PathOfExile2GameState import PathOfExile2GameState
from PathOfExile2Positions import PathOfExile2Positions

class PathOfExile2GameStateReader(IConfigurable):
    def __init__(self, size:Size):
        self.positions = PathOfExile2Positions(size)

    def configure(self, config: ScriptConfig) -> None:
        self.config = config
        self.__dict__.pop("pixels_to_be_read", None)

    @cached_property
    def pixels_to_be_read(self):
        health_pixels=[]
        energy_shield_pixels=[]
        poison_pixel=None
        mana_pixel=None
        rage_pixel=None

        if self.config.configData.chaos_inoculation:
            if self.config.configData.has_runic_ward:
                energy_shield_pixels = self.positions.get_health_pixels_with_runic_ward(self.config.configData.hp_threshold_percent, 0)
            else:
                energy_shield_pixels = [self.positions.get_health_pixel(self.config.configData.hp_threshold_percent, 0)]
        else:
            energy_shield_pixels = [self.positions.get_energy_shield_pixel(self.config.configData.energy_shield_below_bars)]
            if self.config.configData.has_runic_ward:
                health_pixels = self.positions.get_health_pixels_with_runic_ward(self.config.configData.hp_threshold_percent, self.config.configData.health_reservation_percent)
            else:
                health_pixels = [self.positions.get_health_pixel(self.config.configData.hp_threshold_percent, self.config.configData.health_reservation_percent)]
        poison_pixel = self.positions.get_poison_pixel(self.config.configData.hp_threshold_percent, self.config.configData.health_reservation_percent)
        mana_pixel = self.positions.get_mana_pixel(self.config.configData.mana_threshold_percent)
        rage_pixel = self.positions.get_rage_pixel(self.config.configData.rage_threshold_percent)
        
        return health_pixels, energy_shield_pixels, poison_pixel, mana_pixel, rage_pixel

    def read(self) -> tuple[list[RGB], list[RGB], RGB, RGB, RGB]:
        health_pixels, energy_shield_pixels, poison_pixel, mana_pixel, rage_pixel = self.pixels_to_be_read

        points = [*health_pixels, *energy_shield_pixels, poison_pixel, mana_pixel, rage_pixel]
        colors = get_pixels(points)

        health_pixels_rgb = colors[:len(health_pixels)]
        energy_shield_pixels_rgb = colors[len(health_pixels):len(health_pixels) + len(energy_shield_pixels)]
        poison_pixel_rgb = colors[len(health_pixels) + len(energy_shield_pixels)]
        mana_pixel_rgb = colors[len(health_pixels) + len(energy_shield_pixels) + 1]
        rage_pixel_rgb = colors[len(health_pixels) + len(energy_shield_pixels) + 2]

        return health_pixels_rgb, energy_shield_pixels_rgb, poison_pixel_rgb, mana_pixel_rgb, rage_pixel_rgb

    def get_game_state_for_pixel_colors(
        self,
        health_pixels_rgb: list[RGB],
        energy_shield_pixels_rgb: list[RGB],
        poison_pixel_rgb: RGB,
        mana_pixel_rgb: RGB,
        rage_pixel_rgb: RGB,
    ) -> PathOfExile2GameState:
        game_state = PathOfExile2GameState()

        valid_health_pixels_rgb = [color for color in health_pixels_rgb if not is_near_black(color)]
        valid_energy_shield_pixels_rgb = [color for color in energy_shield_pixels_rgb if not is_near_black(color)]

        # Health, Energy Shield, and Poison
        if self.config.configData.chaos_inoculation:
            game_state.is_health_below_threshold = False
            game_state.is_poison = is_pink_color(poison_pixel_rgb)
            if valid_energy_shield_pixels_rgb:
                if game_state.is_poison:
                    game_state.is_energy_shield_below_threshold = not any(is_pink_color(color) for color in valid_energy_shield_pixels_rgb)
                else:
                    game_state.is_energy_shield_below_threshold = not any(is_blue_color(color) for color in valid_energy_shield_pixels_rgb)
        else:
            if valid_energy_shield_pixels_rgb:
                game_state.is_energy_shield_below_threshold = not any(is_blue_color(color) for color in valid_energy_shield_pixels_rgb)
            game_state.is_poison = is_green_color(poison_pixel_rgb)
            game_state.is_shocked = any((is_blue_color(color) or is_white_color(color) or is_purple_color(color)) for color in [*health_pixels_rgb, poison_pixel_rgb])

            if not game_state.is_shocked:
                if valid_health_pixels_rgb:
                    game_state.is_health_below_threshold = not any((is_green_color(color) or is_red_color(color)) for color in valid_health_pixels_rgb)
            else:
                print("Shocked detected, skipping health check.")
                #print([*health_pixels_rgb, poison_pixel_rgb])

        # Mana & Rage
        if not is_near_black(rage_pixel_rgb):
            game_state.is_rage_below_threshold = not is_red_color(rage_pixel_rgb)
        if not is_near_black(mana_pixel_rgb):
            game_state.is_mana_below_threshold = not is_blue_color(mana_pixel_rgb)

        return game_state
