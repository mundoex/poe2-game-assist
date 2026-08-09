from screen_types import Size, Vector2
import math
from PercentToPixelCalculator import PercentToPixelCalculator

MANA_X_CENTER_1920 = 1795
MANA_X_OFFSET_1920 = 1920 - MANA_X_CENTER_1920  #Positive <-
MANA_Y_100_1080 = 890
MANA_Y_0_1080 = 1057

HEALTH_X_CENTER_1920 = 124
HEALTH_X_OFFSET_1920 = HEALTH_X_CENTER_1920 - 1920 #Negative <-
HEALTH_Y_100_1080 = 890
HEALTH_Y_0_1080 = 1057

RAGE_X_100_1920 = 1686
RAGE_X_0_1920 = 1454
RAGE_X_OFFSET_1920 = 1920 - RAGE_X_100_1920
RAGE_Y_1080 = 938

REFERENCE_WIDTH = 1920
REFERENCE_HEIGHT = 1080

RUNIC_WARD_PIXEL_OFFSET = 20
IS_RUNNING_TEXT_OFFSET_X = 20
IS_RUNNING_TEXT_OFFSET_Y = 10

ENERGY_SHIELD_8_8_V2_1920_1080 = (152, 878)
ENERGY_SHIELD_7_8_V2_1920_1080 = (184, 896)
ENERGY_SHIELD_6_8_V2_1920_1080 = (212, 929)
ENERGY_SHIELD_5_8_V2_1920_1080 = (223, 967)
ENERGY_SHIELD_4_8_V2_1920_1080 = (218, 1006)
ENERGY_SHIELD_3_8_V2_1920_1080 = (198, 1039)
ENERGY_SHIELD_2_8_V2_1920_1080 = (168, 1063)
ENERGY_SHIELD_1_8_V2_1920_1080 = (155, 1068)
ENERGY_SHIELD_0_8_V2_1920_1080 = (128, 1073)

ENERGY_SHIELD_8_V2_1920_1080 = {
    8: ENERGY_SHIELD_8_8_V2_1920_1080,
    7: ENERGY_SHIELD_7_8_V2_1920_1080,
    6: ENERGY_SHIELD_6_8_V2_1920_1080,
    5: ENERGY_SHIELD_5_8_V2_1920_1080,
    4: ENERGY_SHIELD_4_8_V2_1920_1080,
    3: ENERGY_SHIELD_3_8_V2_1920_1080,
    2: ENERGY_SHIELD_2_8_V2_1920_1080,
    1: ENERGY_SHIELD_1_8_V2_1920_1080,
    0: ENERGY_SHIELD_0_8_V2_1920_1080,
}

class PathOfExile2Positions:
    def __init__(self, size: Size):
        self.size = size
        self.w = size[0]
        self.h = size[1]

        self.mana_x_center = math.ceil(MANA_X_CENTER_1920 * self.w / REFERENCE_WIDTH)
        self.mana_x_offset = math.ceil(MANA_X_OFFSET_1920 * self.w / REFERENCE_WIDTH)
        self.mana_y_100 = math.ceil(MANA_Y_100_1080 * self.h / REFERENCE_HEIGHT)
        self.mana_y_0 = math.ceil(MANA_Y_0_1080 * self.h / REFERENCE_HEIGHT)

        self.health_x_center = math.ceil(HEALTH_X_CENTER_1920 * self.w / REFERENCE_WIDTH)
        self.health_x_offset = math.ceil(HEALTH_X_OFFSET_1920 * self.w / REFERENCE_WIDTH)
        self.health_y_100 = math.ceil(HEALTH_Y_100_1080 * self.h / REFERENCE_HEIGHT)
        self.health_y_0 = math.ceil(HEALTH_Y_0_1080 * self.h / REFERENCE_HEIGHT)

        self.rage_x_100 = math.ceil(RAGE_X_100_1920 * self.w / REFERENCE_WIDTH)
        self.rage_x_0 = math.ceil(RAGE_X_0_1920 * self.w / REFERENCE_WIDTH)
        self.rage_x_offset = math.ceil(RAGE_X_OFFSET_1920 * self.w / REFERENCE_WIDTH)
        self.rage_y = math.ceil(RAGE_Y_1080 * self.h / REFERENCE_HEIGHT)

        self.energy_shield_bars_v2 = {
            eighths: (math.ceil(x * self.w / REFERENCE_WIDTH), math.ceil(y * self.h / REFERENCE_HEIGHT))
            for eighths, (x, y) in ENERGY_SHIELD_8_V2_1920_1080.items()
        }

        self.mana_calculator = PercentToPixelCalculator([self.mana_x_center, self.mana_y_100], [self.mana_x_center, self.mana_y_0], True)
        self.health_calculator = PercentToPixelCalculator([self.health_x_center, self.health_y_100], [self.health_x_center, self.health_y_0], True)
        self.rage_calculator = PercentToPixelCalculator([self.rage_x_100, self.rage_y], [self.rage_x_0, self.rage_y], True)
    
    def get_mana_pixel(self, percent: float) -> Vector2:
        return self.mana_calculator.get_pixel(percent)

    def get_health_pixel(self, percent: float, health_reservation_percentage: float=0) -> Vector2:
        percent_with_reservation = ((percent/100)*((100-health_reservation_percentage)/100))*100
        return self.health_calculator.get_pixel(percent_with_reservation)

    def get_health_pixels_with_runic_ward(self, percent: float, health_reservation_percentage: float = 0) -> list[Vector2]:
        health_pixel = self.get_health_pixel(percent, health_reservation_percentage)
        return [
            health_pixel,
            (health_pixel[0] + RUNIC_WARD_PIXEL_OFFSET, health_pixel[1]),
            (health_pixel[0] + 2 * RUNIC_WARD_PIXEL_OFFSET, health_pixel[1]),
            (health_pixel[0] + 3 * RUNIC_WARD_PIXEL_OFFSET, health_pixel[1]),
        ]

    def get_rage_pixel(self, percent: float) -> Vector2:
        return self.rage_calculator.get_pixel(percent)

    def get_poison_pixel(self, percent: float, health_reservation_percentage: float=0) -> Vector2:
        return self.get_health_pixel(5, health_reservation_percentage)

    def get_poison_pixel_with_runic_ward(self, percent: float, health_reservation_percentage: float = 0) -> Vector2:
        poison_pixel = self.get_poison_pixel(percent, health_reservation_percentage)
        return (poison_pixel[0] + RUNIC_WARD_PIXEL_OFFSET, poison_pixel[1]),

    def get_energy_shield_pixel(self, eighths: int) -> Vector2:
        return self.energy_shield_bars_v2[eighths]

    def get_top_of_mana_bar(self) -> Vector2:
        return (self.mana_x_center-IS_RUNNING_TEXT_OFFSET_X, self.mana_y_100-IS_RUNNING_TEXT_OFFSET_Y)
    