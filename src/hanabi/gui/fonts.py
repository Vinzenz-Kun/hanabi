"""UI fonts that stay smooth on a high-DPI window and can draw Japanese."""

import os

import pygame
import pygame.freetype

from hanabi.gui.display import Glyph

_SCALE = 1.0
_FACE = None
_CACHE: dict[tuple, Glyph] = {}
_FONTS: dict[int, pygame.freetype.Font] = {}

_CANDIDATES = (
    r"C:\Windows\Fonts\YuGothM.ttc",
    r"C:\Windows\Fonts\YuGothR.ttc",
    r"C:\Windows\Fonts\meiryo.ttc",
    r"C:\Windows\Fonts\segoeui.ttf",
)


def set_scale(scale: float) -> None:
    global _SCALE
    _SCALE = scale
    _CACHE.clear()


def _face() -> str | None:
    global _FACE
    if _FACE is None:
        _FACE = next((path for path in _CANDIDATES if os.path.exists(path)), "")
    return _FACE or None


def _font(pixel_size: int) -> pygame.freetype.Font:
    cached = _FONTS.get(pixel_size)
    if cached is not None:
        return cached
    if not pygame.freetype.get_init():
        pygame.freetype.init()
    face = _face()
    if face:
        font = pygame.freetype.Font(face, pixel_size)
    else:
        font = pygame.freetype.Font(None, pixel_size)
    font.antialiased = True
    font.pad = True
    _FONTS[pixel_size] = font
    return font


class UIFont:
    def __init__(self, size: int) -> None:
        self.size = size

    def render(self, text, antialias=True, color=(255, 255, 255), background=None) -> Glyph:
        label = str(text)
        ink = pygame.Color(color)
        key = (self.size, _SCALE, label, tuple(ink))
        cached = _CACHE.get(key)
        if cached is not None:
            return cached
        if label == "":
            glyph = Glyph(pygame.Surface((1, 1), pygame.SRCALPHA), (0, self.size))
        else:
            pixel_size = max(1, round(self.size * _SCALE))
            big, _ = _font(pixel_size * 2).render(label, ink)
            image = pygame.transform.smoothscale(
                big,
                (max(1, round(big.get_width() / 2)), max(1, round(big.get_height() / 2))),
            )
            logical = (
                max(1, round(image.get_width() / _SCALE)),
                max(1, round(image.get_height() / _SCALE)),
            )
            glyph = Glyph(image, logical)
        if len(_CACHE) > 500:
            _CACHE.clear()
        _CACHE[key] = glyph
        return glyph


def ui_font(size: int) -> UIFont:
    return UIFont(size)
