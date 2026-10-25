"""Night-sky colors and shared drawing for the Hanabi windows."""

import pygame

BG = pygame.Color(16, 8, 32)
INK = pygame.Color(244, 236, 252)
MUTED = pygame.Color(186, 168, 214)
PANEL = pygame.Color(42, 24, 74)
EDGE = pygame.Color(154, 120, 206)
ACCENT = pygame.Color(138, 86, 214)
ACCENT_INK = pygame.Color(248, 242, 255)
GOOD = pygame.Color(86, 164, 124)
GOOD_INK = pygame.Color(14, 32, 24)
DANGER = pygame.Color(176, 72, 112)
FIELD = pygame.Color(58, 36, 98)
GOLD = pygame.Color(214, 186, 248)
QUIET = pygame.Color(68, 42, 108)
SELECTED_INK = pygame.Color(32, 16, 54)

SUITS = {
    "red": pygame.Color(186, 64, 68),
    "blue": pygame.Color(52, 104, 176),
    "green": pygame.Color(42, 138, 96),
    "yellow": pygame.Color(214, 168, 52),
    "white": pygame.Color(236, 230, 216),
    "colorful": pygame.Color(168, 92, 168),
    "gray": pygame.Color(92, 86, 104),
}


def paint(surface: pygame.Surface) -> None:
    surface.fill(BG)


def suit(name: str) -> pygame.Color:
    return SUITS.get(name, SUITS["gray"])


def text(surface, label, font, pos, color=INK) -> None:
    surface.blit(font.render(str(label), True, color), pos)


def panel(surface, rect: pygame.Rect) -> None:
    pygame.draw.rect(surface, PANEL, rect, border_radius=12)
    pygame.draw.rect(surface, EDGE, rect, width=1, border_radius=12)


def button(surface, rect: pygame.Rect, label: str, font, kind: str = "accent") -> None:
    fills = {
        "accent": ACCENT,
        "good": GOOD,
        "danger": DANGER,
        "quiet": QUIET,
        "selected": GOLD,
    }
    inks = {
        "accent": ACCENT_INK,
        "good": GOOD_INK,
        "danger": INK,
        "quiet": INK,
        "selected": SELECTED_INK,
    }
    pygame.draw.rect(surface, fills[kind], rect, border_radius=8)
    pygame.draw.rect(surface, EDGE, rect, width=1, border_radius=8)
    rendered = font.render(str(label), True, inks[kind])
    surface.blit(rendered, rendered.get_rect(center=rect.center))


def field(surface, rect: pygame.Rect, value, font, active: bool = False) -> None:
    pygame.draw.rect(surface, FIELD, rect, border_radius=6)
    pygame.draw.rect(
        surface, GOLD if active else EDGE, rect, width=2 if active else 1, border_radius=6
    )
    rendered = font.render(str(value), True, INK)
    surface.blit(
        rendered, (rect.x + 8, rect.y + (rect.height - rendered.get_height()) // 2)
    )


def card(surface, rect: pygame.Rect, suit_name: str, value, font, show_value: bool = True) -> None:
    pygame.draw.rect(surface, suit(suit_name), rect, border_radius=5)
    pygame.draw.rect(surface, pygame.Color(28, 14, 46), rect, width=1, border_radius=5)
    if show_value and value is not None:
        dark = suit_name in ("white", "yellow")
        ink = pygame.Color(36, 26, 18) if dark else pygame.Color(255, 248, 240)
        rendered = font.render(str(value), True, ink)
        surface.blit(rendered, rendered.get_rect(center=rect.center))


def language_chip(surface, rect: pygame.Rect, font, label: str) -> None:
    button(surface, rect, label, font, "quiet")
