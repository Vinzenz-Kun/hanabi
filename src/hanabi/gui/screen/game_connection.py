import pygame
from hanabi.gui import theme
from hanabi.gui.fonts import ui_font
from hanabi.gui.widgets.colors import Colors as colors


# Implementing the new GameConnectScreen class
class GameConnectScreen:
    def __init__(self, gui) -> None:
        """
        Initializes a new instance of the GameConnectScreen class.

        :param gui: The parent GUI instance.
        :type gui: hanabi.gui.HanabiGUI
        :return: None
        """
        self.gui = gui
        self.font = ui_font(20)
        self.colors = {
            "black": colors.black,
            "white": colors.white,
            "blue": colors.blue,
            "green": colors.green,
            "gray": colors.gray,
            "red": colors.red,
        }
        self.create_ui_elements()

    def create_ui_elements(self) -> None:
        """
        Creates the UI elements for the game connection screen, such as the refresh button, create button, join buttons, and observe buttons.

        :return: None
        """

        self.refresh_button = pygame.Rect(32, 84, 140, 36)
        self.create_button = pygame.Rect(184, 84, 220, 36)
        self.join_buttons = {}
        self.observe_buttons = {}
        self.language_button = pygame.Rect(self.gui.window_width - 200, 20, 180, 40)

    def render(self) -> None:
        """
        Displays a list of available games and options to create or join games.

        :return: None
        """
        theme.paint(self.gui.window)
        pygame.display.set_caption(
            self.gui.language_config.get_translation("game_connect")
        )
        theme.text(
            self.gui.window,
            self.gui.language_config.get_translation("open_games"),
            ui_font(32),
            (32, 24),
            theme.GOLD,
        )
        theme.button(
            self.gui.window,
            self.refresh_button,
            self.gui.language_config.get_translation("refresh"),
            self.font,
            "quiet",
        )
        theme.button(
            self.gui.window,
            self.create_button,
            self.gui.language_config.get_translation("new_game"),
            self.font,
        )

        self.join_buttons.clear()
        self.observe_buttons.clear()
        for i, game_id in enumerate(self.gui.game_ids):
            row = pygame.Rect(32, 140 + i * 52, self.gui.window_width - 64, 44)
            theme.panel(self.gui.window, row)
            theme.text(self.gui.window, f"Game {game_id}", self.font, (row.x + 16, row.y + 10))
            join_button = pygame.Rect(row.right - 250, row.y + 6, 110, 32)
            observe_button = pygame.Rect(row.right - 128, row.y + 6, 110, 32)
            self.join_buttons[f"join_{game_id}"] = join_button
            self.observe_buttons[f"observe_{game_id}"] = observe_button
            theme.button(
                self.gui.window,
                join_button,
                self.gui.language_config.get_translation("join"),
                self.font,
            )
            theme.button(
                self.gui.window,
                observe_button,
                self.gui.language_config.get_translation("observe"),
                self.font,
                "quiet",
            )

        theme.language_chip(
            self.gui.window,
            self.language_button,
            self.font,
            self.gui.language_config.get_translation("Change Language"),
        )

    def handle_input(self, events: list) -> None:
        """
        Processes user input for the game connect screen.

        :param events: A list of pygame events to handle.
        :return: None
        """
        for event in events:
            self.gui.handle_generic_input(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if self.language_button.collidepoint(mouse_pos):
                    self.gui.toggle_language()

                if self.refresh_button.collidepoint(mouse_pos):
                    self.gui.client.logger.info("Clicked Refresh Button")
                    self.gui.client.send_message({"type": "get_games"})

                elif self.create_button.collidepoint(mouse_pos):
                    message = {
                        "type": "create_lobby",
                        "host_username": self.gui.client.username,
                    }
                    self.gui.client.logger.info(
                        f"Clicked Create Button. Sending message: {message}"
                    )
                    self.gui.client.send_message(message)
                    self.gui.client.lobby_settings["game_id"] = self.gui.client.game_id

                else:
                    for game_id in self.gui.game_ids:
                        if self.join_buttons[f"join_{game_id}"].collidepoint(
                            mouse_pos
                        ):  # Join button
                            self.gui.client.join_lobby(game_id)
                            self.gui.current_screen = "lobby"

                        elif self.observe_buttons[f"observe_{game_id}"].collidepoint(
                            mouse_pos
                        ):  # Observe button
                            self.gui.client.observe_lobby(game_id)
                            self.gui.current_screen = "lobby"

            elif event.type == pygame.KEYDOWN and event.key == pygame.K_l:
                self.gui.toggle_language()
