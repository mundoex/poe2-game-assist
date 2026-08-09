import os

import screen_utils_linux as linux
import screen_utils_win as win
from screen_types import Geometry, RGB, Vector2

def get_window_geometry() -> Geometry:
    if os.name == "nt":
        return win.get_window_geometry_windows()
    else:
        return linux.get_window_geometry_by_name_linux("Path of Exile 2")


def get_pixel(x: int, y: int) -> RGB:
    if os.name == "nt":
        return win.get_pixel_windows(x, y)
    else:
        return linux.get_pixel_linux(x, y)
    
def get_pixels(points: list[Vector2]) -> list[RGB]:
    if os.name == "nt":
        return win.get_pixels_windows(points)
    else:
        return linux.get_pixels_linux(points)

def get_window_name() -> str:
    if os.name == "nt":
        return win.get_window_name_windows()
    else:
        return linux.get_window_name_linux()

