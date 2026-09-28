import pygame
from hanabi.gui.fonts import ui_font
import time


class Timer:
    """timer for player turns"""

    def __init__(self) -> None:
        """
        Initializes a Timer object with default settings.

        The timer starts with a default time limit of 2 minutes per turn. The timer is initially inactive.

        :return: None
        """
        self.time_limit = 120  #  Default time limit of 2 minutes per turn
        self.start_time = None
        self.is_active = False
        self.font = ui_font(24)

        self.timer_active = False

        # Colors for different timer states
        self.green = pygame.Color(0, 255, 0)
        self.yellow = pygame.Color(255, 255, 0)
        self.red = pygame.Color(255, 0, 0)
        self.gray = pygame.Color(128, 128, 128)

    def start(self) -> None:
        """
        Start the timer

        :return: None
        """
        self.start_time = time.time()
        self.is_active = True

    def stop(self) -> None:
        """
        Stop the timer

        :return: None
        """
        self.is_active = False
        self.start_time = None

    def restart(self) -> None:
        """
        Restart the timer

        :return: None
        """
        self.stop()
        self.start()

    def get_time_remaining(self) -> float:
        """
        Get remaining time in seconds

        :return: Remaining time in seconds
        """
        if not self.is_active or self.start_time is None:
            return 0

        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)

        # if remaining == 0:
        #    self.stop()

        return remaining

    def time_over(self) -> bool:
        """
        Check if the timer has expired

        :return: True if the timer has expired, False otherwise
        """
        return self.is_active and self.get_time_remaining() <= 0

    def draw(self, window: pygame.Surface, x: int, y: int) -> None:
        """
        Draw the timer on the game window

        :param window: The game window surface
        :param x: The x-coordinate of the timer position
        :param y: The y-coordinate of the timer position
        :return: None
        """
        if not self.is_active:
            return

        remaining = self.get_time_remaining()

        # Choose color based on time remaining
        if remaining > 30:
            color = self.green
        elif remaining > 10:
            color = self.yellow
        else:
            color = self.red

        # Draw timer background
        pygame.draw.rect(window, self.gray, (x, y, 200, 30))

        # Draw timer bar
        width = int((remaining / self.time_limit) * 200)
        pygame.draw.rect(window, color, (x, y, width, 30))

        # Draw time text
        seconds = int(remaining)
        text = f"{seconds}s"
        text_surface = self.font.render(text, True, (255, 255, 255))
        window.blit(text_surface, (x + 85, y + 5))
