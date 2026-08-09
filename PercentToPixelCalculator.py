import math
from screen_types import Vector2

#auto checks if we are calculating for a horizontal or vertical bar based on the pixel_100 and pixel_0 values.
#If the x values are the same, it is a vertical bar, if the y values are the same, it is a horizontal bar.
class PercentToPixelCalculator:
    def __init__(self, pixel_100:Vector2, pixel_0:Vector2, inverted:bool):
        #calculate if x or y is constant
        self.pixel_100 = pixel_100
        self.pixel_0 = pixel_0
        if pixel_100[0] == pixel_0[0]:
            self.const_coord_index = 0
            self.non_const_coord_index = 1
        else:
            self.const_coord_index = 1
            self.non_const_coord_index = 0
        self.c = pixel_0[self.non_const_coord_index]
        self.m = (pixel_100[self.non_const_coord_index] - pixel_0[self.non_const_coord_index]) / 100
        self.inverted = inverted

    def get_pixel(self, percent:float) -> Vector2:
        percent_adjust = percent if self.inverted else 100 - percent
        coord = math.ceil(self.m * percent_adjust + self.c)
        if self.const_coord_index == 0:
            return [self.pixel_0[0], coord]
        else:
            return [coord, self.pixel_0[1]]
