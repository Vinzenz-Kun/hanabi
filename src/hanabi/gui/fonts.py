"""UI fonts that can draw Latin text and Japanese."""

import pygame

_NAMES = "Yu Gothic UI, Yu Gothic, Meiryo, MS Gothic, Noto Sans CJK JP, Arial"


def ui_font(size: int) -> pygame.font.Font:
    return pygame.font.SysFont(_NAMES, size)
