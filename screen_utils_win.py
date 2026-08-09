import ctypes
from screen_types import Geometry, RGB, Vector2

# always assume the window is fullscreen/fullscreen borderless for windows
def get_window_geometry_windows() -> Geometry:
    w = ctypes.windll.user32.GetSystemMetrics(0)
    h = ctypes.windll.user32.GetSystemMetrics(1)
    return 0, 0, w, h


def get_pixel_windows(x: int, y: int) -> RGB:
    dc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(dc, x, y)
    ctypes.windll.user32.ReleaseDC(0, dc)
    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    return r, g, b

def get_pixels_windows(points: list[Vector2]) -> list[RGB]:
    dc = ctypes.windll.user32.GetDC(0)
    colors = []
    for x, y in points:
        color = ctypes.windll.gdi32.GetPixel(dc, x, y)
        r = color & 0xFF
        g = (color >> 8) & 0xFF
        b = (color >> 16) & 0xFF
        colors.append((r, g, b))
    ctypes.windll.user32.ReleaseDC(0, dc)
    return colors

def get_window_name_windows() -> str:
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value
