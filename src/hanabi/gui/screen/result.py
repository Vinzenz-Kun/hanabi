import pygame
import hanabi.utils.lib as lib
from hanabi.gui import theme
from hanabi.gui.fonts import ui_font


class ResultScreen:
    def __init__(self, gui) -> None:
        """
        Initializes the ResultScreen class with default settings and links it to the client.

        :param gui: The parent GUI instance.
        :type gui: hanabi.gui.gui_launcher.GUI
        :return: None
        """
        self.gui = gui
        self.client = gui.client
        self.font = ui_font(20)
        self.colors = {
            "black": pygame.Color(0, 0, 0),
            "white": pygame.Color(255, 255, 255),
            "blue": pygame.Color(0, 0, 255),
            "green": pygame.Color(0, 255, 0),
            "gray": pygame.Color(200, 200, 200),
        }
        self.create_ui_elements()
        self.result_data = None

    def create_ui_elements(self) -> None:
        """
        Creates the UI elements for the result screen, such as the exit button.

        :return: None
        """
        self.exit_button = pygame.Rect(self.gui.window_width // 2 - 110, 420, 220, 44)

    def set_result_data(self, game_over_data) -> None:
        """
        Sets the game result data to be displayed.
        :param game_state: The final state of the game containing score and victory status.
        :return: None
        """
        self.result_data = lib.dict_to_game(game_over_data["game_state"])

    def render(self) -> None:
        """
        Renders the result screen, displaying the final score and a performance message.
        The screen also contains an exit button if the client is the host.

        :return: None
        """
        # Clear screen and set caption
        theme.paint(self.gui.window)
        pygame.display.set_caption(self.gui.language_config.get_translation("end"))
        title = ui_font(40).render(
            self.gui.language_config.get_translation(
                "victory" if self.result_data.is_victory else "game over"
            ),
            True,
            theme.GOLD,
        )
        self.gui.window.blit(
            title, (self.gui.window_width // 2 - title.get_width() // 2, 80)
        )

        if self.result_data:
            # Display the final score
            # score = self.result_data.calculate_score()
            score = self.gui.client.game_state.calculate_score()
            score_text = ui_font(28).render(
                f"{self.gui.language_config.get_translation('score')}: {score}",
                True,
                theme.INK,
            )
            self.gui.window.blit(
                score_text,
                (self.gui.window_width // 2 - score_text.get_width() // 2, 150),
            )

            # Display the performance message based on the score
            performance_message = self.get_performance_message(score)
            performance_text = self.font.render(performance_message, True, theme.MUTED)
            self.gui.window.blit(
                performance_text,
                (self.gui.window_width // 2 - performance_text.get_width() // 2, 200),
            )

        # Display the exit button
        if self.client.status == "host":
            theme.button(
                self.gui.window,
                self.exit_button,
                self.gui.language_config.get_translation("back_to_lobby"),
                self.font,
            )

    def get_performance_message(self, score: int) -> str:
        """
        Returns a performance message based on the final score of the game.

        The messages are translated based on the current language setting.

        :param score: The final score of the game.
        :return: A string containing the performance message.
        """
        if self.result_data.color_rush:
            if score <= 5:
                return self.gui.language_config.get_translation("oje")
            elif 6 <= score <= 10:
                return self.gui.language_config.get_translation("weak")
            elif 11 <= score <= 20:
                return self.gui.language_config.get_translation("ok")
            elif 21 <= score <= 25:
                return self.gui.language_config.get_translation("good")
            elif 26 <= score <= 29:
                return self.gui.language_config.get_translation("great")
            elif score == 30:
                return self.gui.language_config.get_translation("legendary")
            else:
                return self.gui.language_config.get_translation("invalid_score")
        else:
            if score <= 5:
                return self.gui.language_config.get_translation("oje")
            elif 6 <= score <= 10:
                return self.gui.language_config.get_translation("weak")
            elif 11 <= score <= 15:
                return self.gui.language_config.get_translation("ok")
            elif 16 <= score <= 20:
                return self.gui.language_config.get_translation("good")
            elif 21 <= score <= 24:
                return self.gui.language_config.get_translation("great")
            elif score == 25:
                return self.gui.language_config.get_translation("legendary")
            else:
                return self.gui.language_config.get_translation("invalid_score")

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        """
        Handles user input on the result screen.

        Listens for MOUSEBUTTONDOWN events to detect clicks on the exit button.
        If the client is the host, clicking the exit button will transition the
        client back to the lobby screen.

        :param events: A list of pygame events to process.
        :return: None
        """
        for event in events:
            self.gui.handle_generic_input(event)
            if event.type == pygame.MOUSEBUTTONDOWN and self.client.status == "host":
                if self.exit_button.collidepoint(event.pos):
                    self.return_to_lobby()

    def return_to_lobby(self) -> None:
        """
        Handles the transition back to the lobby screen.

        :return: None
        """
        self.gui.client.send_message(
            {
                "type": "return_to_lobby",
                "game_id": self.gui.client.game_id,
                "players": self.gui.client.lobby,
            }
        )
        self.gui.current_screen = "lobby"
