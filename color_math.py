import colorsys

from screen_types import HSV, RGB


def _hue_saturation_deg(rgb: RGB) -> tuple[float, float]:
    r, g, b = rgb
    h, s, _v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360, s


def rgb_to_hsv(rgb: RGB) -> HSV:
    """Convert an RGB color to (hue in degrees 0-360, saturation 0-1, value 0-1)."""
    r, g, b = rgb
    h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
    return h * 360, s, v


def rgb_to_opencv_hsv(rgb: RGB) -> HSV:
    """Convert an RGB color to HSV on OpenCV's scale (H: 0-179, S/V: 0-255), which is what is_red_hsv/is_blue_hsv expect."""
    h_deg, s, v = rgb_to_hsv(rgb)
    return h_deg / 2, s * 255, v * 255


def is_blue_color(rgb: RGB, dominance_threshold=20, min_blue=60) -> bool:
    """Return True if blue is meaningfully stronger than red and not dominated by green (covers cyan-leaning blues)."""
    r, g, b = rgb
    return (
        b >= min_blue
        and b - r >= dominance_threshold
        and g - b <= dominance_threshold
    )


def is_red_color(rgb: RGB, hue_tolerance_deg=30, min_saturation=0.35, min_red=15) -> bool:
    """Return True if hue is close to pure red (0deg), regardless of brightness."""
    r, g, b = rgb
    if r < min_red:
        return False
    hue_deg, saturation = _hue_saturation_deg(rgb)
    hue_distance = min(hue_deg, 360 - hue_deg)
    return hue_distance <= hue_tolerance_deg and saturation >= min_saturation


def is_green_color(rgb: RGB, dominance_threshold=20, min_green=60) -> bool:
    """Return True if green is meaningfully stronger than red and blue."""
    r, g, b = rgb
    return (
        g >= min_green
        and g - r >= dominance_threshold
        and g - b >= dominance_threshold
    )


def is_pink_color(rgb: RGB, min_hue_deg=290, max_hue_deg=345, min_saturation=0.35, min_red=60) -> bool:
    """Return True if hue falls in the magenta/pink band, away from pure red."""
    r, g, b = rgb
    if r < min_red:
        return False
    hue_deg, saturation = _hue_saturation_deg(rgb)
    return min_hue_deg <= hue_deg <= max_hue_deg and saturation >= min_saturation


def is_white_color(rgb: RGB, min_brightness=200, max_channel_spread=15) -> bool:
    """Return True if all channels are bright and close together (no dominant hue)."""
    r, g, b = rgb
    return (
        min(r, g, b) >= min_brightness
        and max(r, g, b) - min(r, g, b) <= max_channel_spread
    )

def is_red_hsv(hsv: HSV) -> bool:
    h, s, v = hsv

    return (
        ((0 <= h <= 14) or (176 <= h <= 180))
        and s >= 45
        and v >= 10
    )


def is_blue_hsv(hsv: HSV) -> bool:
    h, s, v = hsv

    return (
        (85 <= h <= 130)
        and s >= 45
        and v >= 10
    )