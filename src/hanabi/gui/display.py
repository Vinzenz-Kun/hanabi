"""Open a sharp window on high-DPI displays.

Screens keep laying out a 900 by 800 board. This module stretches that board
with whole pixels onto the real monitor, instead of letting Windows scale a
blurry copy.
"""

import ctypes
import os

os.environ.setdefault("SDL_WINDOWS_DPI_AWARENESS", "permonitorv2")

import pygame

SCALE = 1.0
_DRAW_PATCHED = False
_ORIG_RECT = pygame.draw.rect


class Glyph:
    """Text already rasterized at the window's real pixel size."""

    def __init__(self, image: pygame.Surface, logical_size: tuple[int, int]) -> None:
        self.image = image
        self._size = logical_size

    def get_width(self) -> int:
        return self._size[0]

    def get_height(self) -> int:
        return self._size[1]

    def get_size(self) -> tuple[int, int]:
        return self._size

    def get_rect(self, **kwargs) -> pygame.Rect:
        rect = pygame.Rect(0, 0, *self._size)
        for key, value in kwargs.items():
            setattr(rect, key, value)
        return rect


class UICanvas:
    """Logical drawing surface. Coordinates stay in the 900 by 800 layout."""

    def __init__(self, surface: pygame.Surface, scale: float) -> None:
        self.surface = surface
        self.scale = scale

    def fill(self, color) -> None:
        self.surface.fill(color)

    def blit(self, source, dest, area=None, special_flags=0) -> pygame.Rect:
        if isinstance(source, Glyph):
            image = source.image
        else:
            width = max(1, round(source.get_width() * self.scale))
            height = max(1, round(source.get_height() * self.scale))
            image = source
            if (width, height) != source.get_size():
                image = pygame.transform.smoothscale(source, (width, height))
        return self.surface.blit(image, _scale_point(dest, self.scale), area, special_flags)

    def get_width(self) -> int:
        return round(self.surface.get_width() / self.scale)

    def get_height(self) -> int:
        return round(self.surface.get_height() / self.scale)


def enable_dpi_awareness() -> None:
    if os.name != "nt":
        return
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            return


def choose_scale(logical_w: int, logical_h: int) -> float:
    if os.name != "nt":
        return 1.0
    screen_w = ctypes.windll.user32.GetSystemMetrics(0)
    screen_h = ctypes.windll.user32.GetSystemMetrics(1)
    fit = min((screen_w * 0.86) / logical_w, (screen_h * 0.86) / logical_h)
    for step in (2.5, 2.0, 1.75, 1.5, 1.25):
        if step <= fit + 0.02:
            return step
    return 1.0


def init_window(logical_w: int, logical_h: int) -> UICanvas:
    global SCALE
    enable_dpi_awareness()
    pygame.init()
    pygame.font.init()
    SCALE = choose_scale(logical_w, logical_h)
    from hanabi.gui.fonts import set_scale

    set_scale(SCALE)
    screen = pygame.display.set_mode((round(logical_w * SCALE), round(logical_h * SCALE)))
    _install_draw_patch()
    return UICanvas(screen, SCALE)


def scale_event(event: pygame.event.Event) -> pygame.event.Event:
    if event.type not in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
        return event
    data = event.dict.copy()
    x, y = event.pos
    data["pos"] = (x / SCALE, y / SCALE)
    return pygame.event.Event(event.type, data)


def _scale_point(dest, scale: float):
    if isinstance(dest, pygame.Rect):
        return (round(dest.x * scale), round(dest.y * scale))
    return (round(dest[0] * scale), round(dest[1] * scale))


def _scale_rect(rect, scale: float) -> pygame.Rect:
    source = pygame.Rect(rect)
    return pygame.Rect(
        round(source.x * scale),
        round(source.y * scale),
        max(1, round(source.w * scale)),
        max(1, round(source.h * scale)),
    )


def _install_draw_patch() -> None:
    global _DRAW_PATCHED
    if _DRAW_PATCHED:
        return

    def rect(surface, color, area, *args, **kwargs):
        target = surface
        if isinstance(surface, UICanvas):
            target = surface.surface
            area = _scale_rect(area, surface.scale)
            args, kwargs = _scale_stroke(args, kwargs, surface.scale)
        return _ORIG_RECT(target, color, area, *args, **kwargs)

    pygame.draw.rect = rect
    _DRAW_PATCHED = True


def _scale_stroke(args, kwargs, scale: float):
    scaled_args = list(args)
    if scaled_args and scaled_args[0]:
        scaled_args[0] = max(1, round(scaled_args[0] * scale))
    if kwargs.get("width"):
        kwargs["width"] = max(1, round(kwargs["width"] * scale))
    for key in (
        "border_radius",
        "border_top_left_radius",
        "border_top_right_radius",
        "border_bottom_left_radius",
        "border_bottom_right_radius",
    ):
        value = kwargs.get(key, -1)
        if value not in (-1, 0):
            kwargs[key] = max(1, round(value * scale))
    return tuple(scaled_args), kwargs
