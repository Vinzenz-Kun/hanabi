import pygame
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
        self.font = pygame.font.SysFont("times new roman", 20)
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

        self.refresh_button = pygame.Rect(23, 50, 120, 30)
        self.create_button = pygame.Rect(150, 50, 180, 30)
        self.join_buttons = {}
        self.observe_buttons = {}
        self.language_button = pygame.Rect(self.gui.window_width - 200, 20, 180, 40)

    def render(self) -> None:
        """
        Displays a list of available games and options to create or join games.

        :return: None
        """
        self.gui.window.fill(self.colors["black"])
        pygame.display.set_caption(
            self.gui.language_config.get_translation("game_connect")
        )
        title = self.font.render(
            self.gui.language_config.get_translation("open_games"),
            True,
            self.colors["white"],
        )
        self.gui.window.blit(title, (20, 20))

        # Refresh Button
        pygame.draw.rect(self.gui.window, self.colors["green"], self.refresh_button)
        refresh_text = self.font.render(
            self.gui.language_config.get_translation("refresh"),
            True,
            self.colors["black"],
        )
        self.gui.window.blit(refresh_text, (30, 55))

        # Create Game Button
        pygame.draw.rect(self.gui.window, self.colors["green"], self.create_button)
        create_text = self.font.render(
            self.gui.language_config.get_translation("new_game"),
            True,
            self.colors["black"],
        )
        self.gui.window.blit(create_text, (150, 55))

        # Display available games
        self.join_buttons.clear()
        self.observe_buttons.clear()
        for i, game_id in enumerate(self.gui.game_ids):
            game_text = self.font.render(
                f"Game ID: {game_id}", True, self.colors["white"]
            )
            self.gui.window.blit(game_text, (20, 100 + i * 30))

            # Join button for each game
            join_button = pygame.Rect(200, 100 + i * 30, 100, 20)
            self.join_buttons[f"join_{game_id}"] = join_button
            pygame.draw.rect(self.gui.window, self.colors["blue"], join_button)
            join_text = self.font.render(
                self.gui.language_config.get_translation("join"),
                True,
                self.colors["white"],
            )
            self.gui.window.blit(join_text, (join_button.x + 10, join_button.y))

            # Observe button for each game
            observe_button = pygame.Rect(join_button.right + 10, 100 + i * 30, 100, 20)
            self.observe_buttons[f"observe_{game_id}"] = observe_button
            pygame.draw.rect(self.gui.window, self.colors["gray"], observe_button)
            observe_text = self.font.render(
                self.gui.language_config.get_translation("observe"),
                True,
                self.colors["white"],
            )
            self.gui.window.blit(
                observe_text, (observe_button.x + 10, observe_button.y)
            )

        pygame.draw.rect(self.gui.window, (200, 200, 200), self.language_button)
        language_text = self.font.render(
            self.gui.language_config.get_translation("Change Language"), True, (0, 0, 0)
        )
        self.gui.window.blit(language_text, (self.gui.window_width - 190, 30))

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
