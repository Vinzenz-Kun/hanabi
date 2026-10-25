import pygame

from hanabi.gui import theme
from hanabi.gui.fonts import ui_font
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

        theme.paint(self.gui.window)
        pygame.display.set_caption(self.gui.language_config.get_translation("lobby"))
        title = ui_font(28).render(
            f"Lobby  ·  {self.gui.client.game_id}", True, theme.GOLD
        )
        self.gui.window.blit(title, (32, 18))

        # Check if lobby exists and has players
        if self.gui.client.lobby and len(self.gui.client.lobby) > 0:
            # Display current players
            y = 110
            x = 50
            for player in self.gui.client.lobby:
                theme.text(
                    self.gui.window,
                    f"{self.gui.language_config.get_translation('player')}: {player}",
                    self.font,
                    (x, y),
                )
                y += 30
                # y += 40
            if 6 > len(self.gui.client.lobby) > 1:
                status = self.gui.language_config.get_translation("ready")
                status_color = theme.GOOD
            elif len(self.gui.client.lobby) > 5:
                status = self.gui.language_config.get_translation("overcrowded")
                status_color = theme.DANGER
            else:
                status = self.gui.language_config.get_translation("not_enough")
                status_color = theme.DANGER
            theme.text(self.gui.window, status, self.font, (50, 64), status_color)

            if self.gui.client.username == self.gui.client.lobby[0]:
                theme.text(
                    self.gui.window,
                    self.gui.language_config.get_translation("game_settings"),
                    self.font,
                    (50, y),
                    theme.GOLD,
                )
                y += 30

                # Storm Tokens
                theme.text(
                    self.gui.window,
                    self.gui.language_config.get_translation("storm_tokens"),
                    self.font,
                    (50, y),
                )
                self.storm_buttons = self.draw_parameter_buttons(
                    250, y, range(1, 4), "storm_tokens"
                )
                y += 50

                # Hint Tokens
                theme.text(
                    self.gui.window,
                    self.gui.language_config.get_translation("hints"),
                    self.font,
                    (50, y),
                )
                self.hint_buttons = self.draw_parameter_buttons(
                    250, y, range(1, 13), "hint_tokens"
                )
                y += 70

                # Timer Settings
                self.timer_button.y = y
                self.timer_input.y = y
                timer_active = self.gui.client.lobby_settings.get("timer_active", False)
                theme.button(
                    self.gui.window,
                    self.timer_button,
                    self.gui.language_config.get_translation("activate_timer"),
                    self.gui.font_small,
                    "good" if timer_active else "quiet",
                )
                theme.field(
                    self.gui.window,
                    self.timer_input,
                    self.timer_seconds,
                    self.font,
                    self.timer_input_active,
                )
                y += 70

                # Color Rush Activation Button TODO: Implement functionality
                self.color_rush_button = pygame.Rect(225, y, 200, 40)
                color_rush_active = self.gui.client.lobby_settings.get(
                    "color_rush", False
                )
                theme.button(
                    self.gui.window,
                    self.color_rush_button,
                    self.gui.language_config.get_translation("activate_color_rush"),
                    self.gui.font_small,
                    "good" if color_rush_active else "quiet",
                )

                self.start_game_button = pygame.Rect(50, y, 160, 40)
                theme.button(
                    self.gui.window,
                    self.start_game_button,
                    self.gui.language_config.get_translation("start_game"),
                    self.font,
                )

                # Displaying saved games, if there are any
                saved_games = GameStateManager.get_saved_games()
                for game_file in saved_games:
                    button_rect = pygame.Rect(450, y, 200, 40)
                    self.saved_games_buttons[game_file] = button_rect
                    theme.button(
                        self.gui.window,
                        button_rect,
                        f"{self.gui.language_config.get_translation('load_save')}: {game_file}",
                        self.gui.font_small,
                        "selected" if self.actitve_saved_game == game_file else "quiet",
                    )

                    player_list_text = ", ".join(
                        GameStateManager.get_players(game_file)
                    )
                    player_text = self.gui.font_small.render(
                        player_list_text, True, theme.MUTED
                    )
                    self.gui.window.blit(player_text, (button_rect.x + 300, y + 5))

                    y += 40

        theme.language_chip(
            self.gui.window,
            self.language_button,
            self.gui.font_small,
            self.gui.language_config.get_translation("Change Language"),
        )

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
            theme.button(
                self.gui.window,
                button_rect,
                str(value),
                self.gui.font_small,
                "selected" if self.gui.client.lobby_settings[parameter_name] == value else "quiet",
            )
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
