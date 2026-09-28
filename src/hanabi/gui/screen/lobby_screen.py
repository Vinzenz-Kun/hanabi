import pygame

from hanabi.gui.widgets.colors import Colors as colors
from hanabi.utils.state_manager import GameStateManager


class LobbyScreen:
    def __init__(self, gui) -> None:
        """
        Initializes the LobbyScreen class with default settings and links it to the client.

        :param gui: The parent GUI instance.
        :type gui: hanabi.gui.gui_launcher.GUI
        :return: None
        """
        self.gui = gui
        self.font = self.gui.font
        self.colors = {
            "black": colors.black,
            "white": colors.white,
            "blue": colors.blue,
            "green": colors.green,
            "gray": colors.gray,
            "red": colors.red,
        }
        self.create_ui_elements()
        self.gui.language_config = self.gui.language_config
        self.timer_active = False
        self.timer_seconds = "60"
        self.timer_input_active = False

    def create_ui_elements(self) -> None:
        """
        Creates the UI elements for the lobby screen, including the start button, refresh button, color rush button, and player list.

        :return: None
        """
        self.start_button = pygame.Rect(20, 50, 140, 40)
        self.refresh_button = pygame.Rect(180, 50, 140, 40)
        self.storm_buttons = []
        self.hint_buttons = []
        self.color_rush_button = pygame.Rect(170, 50, 140, 40)
        self.timer_button = pygame.Rect(
            225, 0, 200, 40
        )  # Will be positioned dynamically
        self.timer_input = pygame.Rect(450, 0, 100, 40)
        self.player_list = []
        self.saved_games_buttons = {}
        self.actitve_saved_game = None
        self.update_host_settings()
        self.language_button = pygame.Rect(self.gui.window_width - 200, 20, 180, 40)

    def update_host_settings(self) -> None:
        """
        Updates the local copy of lobby settings from the client.

        :return: None
        """
        self.storm_tokens = self.gui.client.lobby_settings["storm_tokens"]
        self.hint_tokens = self.gui.client.lobby_settings["hint_tokens"]
        self.color_rush = self.gui.client.lobby_settings.get("color_rush", False)
        if "timer_active" not in self.gui.client.lobby_settings:
            self.timer_active = self.gui.client.lobby_settings["timer_active"]
            self.timer_seconds = self.gui.client.lobby_settings["timer_seconds"]

    def render(self) -> None:
        """
        Displays the lobby with additional options for the host.

        :return: None
        """

        self.gui.window.fill(self.colors["black"])
        pygame.display.set_caption(self.gui.language_config.get_translation("lobby"))
        title = self.font.render(
            f"Lobby - Game ID: {self.gui.client.game_id}", True, self.colors["white"]
        )
        self.gui.window.blit(title, (20, 20))

        # Check if lobby exists and has players
        if self.gui.client.lobby and len(self.gui.client.lobby) > 0:
            # Display current players
            y = 100
            x = 50
            for player in self.gui.client.lobby:
                player_text = self.font.render(
                    f"{self.gui.language_config.get_translation('player')}: {player}",
                    True,
                    self.colors["white"],
                )
                self.gui.window.blit(player_text, (x, y))
                y += 30
                # y += 40
            if 6 > len(self.gui.client.lobby) > 1:
                # If lobby has the right amount of players
                error_text = self.font.render(
                    self.gui.language_config.get_translation("ready"),
                    True,
                    self.colors["green"],
                )
                self.gui.window.blit(error_text, (50, 70))

            elif len(self.gui.client.lobby) > 5:
                # If lobby is overcrowded
                error_text = self.font.render(
                    self.gui.language_config.get_translation("overcrowded"),
                    True,
                    self.colors["red"],
                )
                self.gui.window.blit(error_text, (50, 70))
            else:
                # If lobby has not enough players
                error_text = self.font.render(
                    self.gui.language_config.get_translation("not_enough"),
                    True,
                    self.colors["red"],
                )
                self.gui.window.blit(error_text, (50, 70))

            if self.gui.client.username == self.gui.client.lobby[0]:
                self.gui.window.blit(
                    self.font.render(
                        self.gui.language_config.get_translation("game_settings"),
                        True,
                        self.colors["green"],
                    ),
                    (50, y),
                )
                y += 30

                # Storm Tokens
                storm_text = self.font.render(
                    self.gui.language_config.get_translation("storm_tokens"),
                    True,
                    self.colors["white"],
                )
                self.gui.window.blit(storm_text, (50, y))
                self.storm_buttons = self.draw_parameter_buttons(
                    250, y, range(1, 4), "storm_tokens"
                )
                y += 50

                # Hint Tokens
                hint_text = self.font.render(
                    self.gui.language_config.get_translation("hints"),
                    True,
                    self.colors["white"],
                )
                self.gui.window.blit(hint_text, (50, y))
                self.hint_buttons = self.draw_parameter_buttons(
                    250, y, range(1, 13), "hint_tokens"
                )
                y += 70

                # Timer Settings
                self.timer_button.y = y
                self.timer_input.y = y
                timer_active = self.gui.client.lobby_settings.get("timer_active", False)
                timer_button_color = (
                    self.colors["green"] if timer_active else self.colors["red"]
                )
                pygame.draw.rect(self.gui.window, timer_button_color, self.timer_button)
                timer_text = self.font.render(
                    self.gui.language_config.get_translation("activate_timer"),
                    True,
                    self.colors["black"],
                )
                self.gui.window.blit(
                    timer_text, (self.timer_button.x + 20, self.timer_button.y + 5)
                )

                # Timer Input Field
                pygame.draw.rect(
                    self.gui.window, self.colors["white"], self.timer_input
                )
                timer_value = self.font.render(
                    str(self.timer_seconds), True, self.colors["black"]
                )
                self.gui.window.blit(
                    timer_value, (self.timer_input.x + 10, self.timer_input.y + 5)
                )
                y += 70

                # Color Rush Activation Button TODO: Implement functionality
                self.color_rush_button = pygame.Rect(225, y, 200, 40)
                color_rush_active = self.gui.client.lobby_settings.get(
                    "color_rush", False
                )
                color_rush_button_color = (
                    self.colors["green"] if color_rush_active else self.colors["red"]
                )
                pygame.draw.rect(
                    self.gui.window, color_rush_button_color, self.color_rush_button
                )
                color_rush_text = self.font.render(
                    self.gui.language_config.get_translation("activate_color_rush"),
                    True,
                    self.colors["black"],
                )
                self.gui.window.blit(
                    color_rush_text,
                    (self.color_rush_button.x + 20, self.color_rush_button.y + 5),
                )

                # Start Game Button
                self.start_game_button = pygame.Rect(50, y, 150, 40)
                pygame.draw.rect(
                    self.gui.window, self.colors["green"], self.start_game_button
                )
                start_text = self.font.render(
                    self.gui.language_config.get_translation("start_game"),
                    True,
                    self.colors["black"],
                )
                self.gui.window.blit(
                    start_text,
                    (self.start_game_button.x + 20, self.start_game_button.y + 5),
                )

                # Displaying saved games, if there are any
                saved_games = GameStateManager.get_saved_games()
                for game_file in saved_games:
                    button_rect = pygame.Rect(450, y, 200, 40)
                    self.saved_games_buttons[game_file] = button_rect
                    color = (
                        self.colors["green"]
                        if self.actitve_saved_game == game_file
                        else self.colors["red"]
                    )
                    pygame.draw.rect(self.gui.window, color, button_rect)
                    button_text = self.font.render(
                        f"Laden: {game_file}", True, self.colors["black"]
                    )
                    self.gui.window.blit(
                        button_text, (button_rect.x + 10, button_rect.y + 5)
                    )

                    # Draw the expected players next to the button
                    player_list_text = ", ".join(
                        GameStateManager.get_players(game_file)
                    )
                    player_text = self.gui.font_small.render(
                        player_list_text, True, self.colors["white"]
                    )
                    self.gui.window.blit(player_text, (button_rect.x + 300, y + 5))

                    y += 40

        pygame.draw.rect(self.gui.window, (200, 200, 200), self.language_button)
        language_text = self.font.render(
            self.gui.language_config.get_translation("Change Language"), True, (0, 0, 0)
        )
        self.gui.window.blit(language_text, (self.gui.window_width - 190, 30))

    def draw_parameter_buttons(
        self, x: int, y: int, values: list, parameter_name: str
    ) -> list:
        """
        Draws buttons for selecting parameter values.

        :param x: The x-coordinate for the buttons.
        :param y: The y-coordinate for the buttons.
        :param values: The list of values to display as buttons.
        :param parameter_name: The name of the parameter being adjusted.
        :return: A list of pygame.Rect objects representing the buttons.
        """
        buttons = []
        for value in values:
            button_rect = pygame.Rect(x, y, 40, 30)
            if self.gui.client.lobby_settings[parameter_name] == value:
                pygame.draw.rect(
                    self.gui.window, self.colors["green"], button_rect
                )  # Highlight selected
            else:
                pygame.draw.rect(
                    self.gui.window, self.colors["gray"], button_rect
                )  # Default button color
            value_text = self.font.render(str(value), True, self.colors["black"])
            self.gui.window.blit(value_text, (button_rect.x + 10, button_rect.y + 5))
            buttons.append((button_rect, value))
            x += 50
        return buttons

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        """
        Handles user input in the lobby screen.

        :return: None
        """
        for event in events:
            self.gui.handle_generic_input(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos

                if self.language_button.collidepoint(mouse_pos):
                    self.gui.toggle_language()

                if (
                    self.gui.client.lobby
                    and self.gui.client.username == self.gui.client.lobby[0]
                ):

                    # Timer Input Field Click
                    if self.timer_input.collidepoint(mouse_pos):
                        self.timer_input_active = True
                    else:
                        self.timer_input_active = False

                    # Timer Button Click
                    if self.timer_button.collidepoint(mouse_pos):
                        self.timer_active = not self.timer_active
                        self.gui.client.lobby_settings["timer_active"] = (
                            not self.gui.client.lobby_settings.get(
                                "timer_active", False
                            )
                        )
                        if self.timer_seconds:
                            self.gui.client.lobby_settings["timer_seconds"] = int(
                                self.timer_seconds
                            )
                        else:
                            self.gui.client.lobby_settings["timer_seconds"] = 60

                    # Modify Storm Tokens
                    for button_rect, value in self.storm_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            self.gui.client.lobby_settings["storm_tokens"] = value
                            self.gui.client.logger.info(
                                f"Selected Storm Tokens: {value}"
                            )

                    # Modify Hint Tokens
                    for button_rect, value in self.hint_buttons:
                        if button_rect.collidepoint(mouse_pos):
                            self.gui.client.lobby_settings["hint_tokens"] = value
                            self.gui.client.logger.info(
                                f"Selected Hint Tokens: {value}"
                            )

                    # Toggle Color Rush
                    if self.color_rush_button.collidepoint(mouse_pos):
                        self.gui.client.lobby_settings["color_rush"] = (
                            not self.gui.client.lobby_settings["color_rush"]
                        )

                    # Start the game
                    if self.start_game_button.collidepoint(mouse_pos):
                        # self.client.finalize_lobby(self.client.lobby_settings)
                        if self.actitve_saved_game is not None:
                            self.gui.client.game_state = (
                                GameStateManager.load_game_state(
                                    self.actitve_saved_game
                                )
                            )
                        self.gui.client.lobby_settings["timer_seconds"] = int(
                            self.timer_seconds
                        )
                        self.gui.client.lobby_settings["timer_active"] = (
                            self.timer_active
                        )
                        self.gui.screens["game"].timer.time_limit = (
                            self.gui.client.lobby_settings.get("timer_seconds")
                        )
                        self.gui.screens["game"].timer.timer_active = (
                            self.gui.client.lobby_settings.get("timer_active")
                        )
                        self.gui.client.logger.info(f"Timer: {self.timer_seconds}")
                        self.gui.client.finalize_lobby()
                        self.gui.client.logger.info(
                            "Game settings finalized, starting the game."
                        )

                    # Select a saved game
                    for game_file, button_rect in self.saved_games_buttons.items():
                        if button_rect.collidepoint(mouse_pos):
                            if self.actitve_saved_game == game_file:
                                self.actitve_saved_game = None
                                break
                            else:
                                self.actitve_saved_game = game_file
                                self.gui.load_game(game_file)
                                break
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_l:
                    self.gui.toggle_language()
                elif self.timer_input_active:
                    if event.key == pygame.K_RETURN:
                        self.timer_input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.timer_seconds = self.timer_seconds[:-1]
                    elif event.unicode.isnumeric():
                        self.timer_seconds = (self.timer_seconds + event.unicode)[:3]
                        if self.timer_seconds and int(self.timer_seconds) > 999:
                            self.timer_seconds = "999"
