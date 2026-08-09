import os
import re
import subprocess
import tempfile

from PIL import Image

from screen_types import Geometry, RGB

def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)

def get_window_id_by_name(name: str) -> str:
    out = sh(["xwininfo", "-name", name])
    m = re.search(r"Window id:\s+(0x[0-9a-fA-F]+)", out)
    if not m:
        raise RuntimeError(f'Could not find window with name "{name}"')
    return m.group(1)

def get_window_geometry_by_id_linux(win_id: str) -> Geometry:
    # xwininfo -id ... prints Absolute upper-left X/Y and Width/Height
    out = sh(["xwininfo", "-id", win_id])

    def grab(pattern: str) -> int | None:
        m = re.search(pattern, out)
        return int(m.group(1)) if m else None

    x = grab(r"Absolute upper-left X:\s+(-?\d+)")
    y = grab(r"Absolute upper-left Y:\s+(-?\d+)")
    w = grab(r"Width:\s+(\d+)")
    h = grab(r"Height:\s+(\d+)")

    if None in (x, y, w, h):
        raise RuntimeError("Failed to parse xwininfo geometry. Raw output:\n" + out)

    return x, y, w, h

def get_window_geometry_by_name_linux(name: str) -> Geometry:
    win_id = get_window_id_by_name(name)
    return get_window_geometry_by_id_linux(win_id)


def get_pixel_linux(x: int, y: int) -> RGB:
    wx, wy, ww, wh = get_window_geometry_by_name_linux("Path of Exile 2")
    if not (0 <= x < ww and 0 <= y < wh):
        raise ValueError("Pixel out of window bounds")

    # Absolute screen coordinates of the pixel
    sx, sy = wx + x, wy + y

    # Use import to capture a 1x1 region (and output color)
    # -format %[pixel:u] returns pixel color as "srgb(r,g,b)" in many builds; we convert by asking for exact channels.
    # We'll output as "r g b" via %[fx:...] is tricky; simplest: capture 1x1 png then read with PIL.
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "p.png")
        cmd = [
            "import",
            "-window", "root",
            "-crop", "1x1+{}+{}".format(sx, sy),
            "png:" + path
        ]
        # Note: import syntax can vary; if this complains, tell me the error.
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)

        img = Image.open(path).convert("RGB")
        return img.getpixel((0, 0))


def get_window_name_linux() -> str:
    try:
        wid = sh(["xdotool", "getactivewindow"]).strip()
        return sh(["xdotool", "getwindowname", wid]).strip()
    except Exception:
        return ""

def get_pixels_linux(points: list[tuple[int, int]]) -> list[RGB]:
    raise NotImplementedError("get_pixels_linux is not implemented for Linux. Use get_pixel_linux in a loop instead.")