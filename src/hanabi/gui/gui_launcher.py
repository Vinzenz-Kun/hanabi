from hanabi.gui.widgets.cardselection import CardSelection
import pygame  # type: ignore
from hanabi.gui.screen.server_connection import ServerConnectScreen
from hanabi.gui.screen.game_connection import GameConnectScreen
from hanabi.gui.screen.lobby_screen import LobbyScreen
from hanabi.gui.screen.game_screen import GameScreen
from hanabi.gui.screen.result import ResultScreen
from hanabi.gui.fonts import ui_font
from hanabi.gui.language_config import LanguageConfig
from hanabi.gui.screen.menu import MenuScreen
from hanabi.utils.state_manager import GameStateManager


class GUI:
    def __init__(self, client) -> None:
        """
        Initializes the GUI with default settings and links it to the client.

        :param client: The Client object to communicate with the server
        :type client: hanabi.core.client_launcher.Client
        :return: None
        """
        pygame.init()
        self.client = client
        self.language_config = LanguageConfig()
        self.window_width = 900
        self.window_height = 800
        self.font = ui_font(20)
        self.font_small = ui_font(14)
        self.window = pygame.display.set_mode((self.window_width, self.window_height))
        self.running = True
        self.current_screen = "server_connect"
        self.screens = {
            "server_connect": ServerConnectScreen(self),
            "game_connect": GameConnectScreen(self),
            "lobby": LobbyScreen(self),
            "game": GameScreen(self),
            "result": ResultScreen(self),
            "menu": MenuScreen(self),
        }
        self.language_config = self.initialize_language_config()
        self.clock = pygame.time.Clock()
        self.game_ids = []
        self.visited_screens = ["server_connect"]
        self.popup_message = None

    def initialize_language_config(self) -> LanguageConfig:
        """
        Initializes the LanguageConfig object, which stores the current language
        and translations for the GUI. The LanguageConfig object is used by the
        GUI to render text in the correct language.

        :return: The LanguageConfig object
        """
        from hanabi.gui.language_config import LanguageConfig

        return LanguageConfig()

    def update_display(self) -> None:
        """
        Updates the display by rendering the current screen and handling any user input.
        It retrieves any user input events from the event queue, passes
        them to the current screen for handling, and then renders the current screen to the display.

        :return: None
        """
        events = pygame.event.get()
        if self.current_screen in self.screens:
            self.screens[self.current_screen].handle_input(events)
            self.screens[self.current_screen].render()

        if self.popup_message and pygame.time.get_ticks() < self.popup_timer:
            self.display_popup(self.popup_message)
        else:
            self.popup_message = None

    def toggle_language(self) -> None:
        """
        Cycles the interface through English, German, and Japanese.

        :return: None
        """
        self.language_config.cycle_language()

    def handle_generic_input(self, event: pygame.event) -> None:
        """
        Handles generic input events such as closing the window, pressing the Escape key to toggle the overlay menu, and pressing the 'L' key to toggle the language.

        :param event: The event to handle
        :return: None
        """
        if event.type == pygame.QUIT:
            self.client.handle_disconnect()
            # self.client.disconnect_from_server()
            self.running = False
        elif (
            event.type == pygame.KEYDOWN
            and event.key == pygame.K_ESCAPE
            and self.current_screen != "game_screen"
        ):
            # Toggle the overlay menu when Escape is pressed
            if self.current_screen != "menu":
                self.current_screen = "menu"
            else:
                self.current_screen = self.visited_screens[-1]
        elif (
            event.type == pygame.KEYDOWN and event.key == pygame.K_l
        ):  # 'L' key to toggle language
            self.toggle_language()
            self.update_display()

    def handle_error(self, error_message: str) -> None:
        """
        Handles game-related errors by displaying a message and transitioning to the menu screen.

        :param error_message: The error message to display
        :return: None
        """
        self.client.logger.error(
            f"Error: {error_message}. Tranistioning to menu screen.\n"
        )
        if "disconnected" in error_message.lower():
            self.current_screen = "menu"
            self.screens["menu"].render()

    def run(self) -> None:
        """
        Main loop for the GUI.

        Continuously updates the display, processes events, and maintains a consistent frame rate
        while the application is running.

        :return: None
        """
        while self.running:
            self.update_display()
            pygame.display.update()
            self.clock.tick(30)

    def add_log_message(self, message: list) -> None:
        """
        Adds a new log message to the game's log block.

        :param message: A list of strings, with the first string being the player name,
            the second string being the action, the third string being the card played,
            and the fourth string being the message.
        :return: None
        """
        GameScreen.add_log_message(message)

    def load_game(self, game_file: dict) -> None:
        """
        Loads a saved game state from a file and updates the current game and lobby.

        :param game_file: The filename of the saved game state to load.
        :return: None
        """
        try:
            loaded_game = GameStateManager.load_game_state(game_file)
            loaded_game["game_ID"] = self.client.game_id  # Preserve the current lobby

            existing_players = self.client.lobby
            new_players = [player["name"] for player in loaded_game["players"]]
            # if existing_players == new_players:
            for player in new_players:
                if player not in existing_players:
                    self.show_popup(
                        f"{self.language_config.get_translation('player_mismatch')}"
                    )
                    self.screens["lobby"].active_saved_game = None
                    return
            self.current_game = loaded_game
            self.client.lobby = [player["name"] for player in loaded_game["players"]]
            self.show_popup(
                f"{self.language_config.get_translation('game_loaded')}: {game_file}"
            )
            # else:
            #     self.show_popup(f"{self.language_config.get_translation('player_mismatch')}")
            #     self.screens['lobby'].active_saved_game = None
        except FileNotFoundError as e:
            self.client.logger.error(f"Error loading the game: {str(e)}")
            self.screens["lobby"].active_saved_game = None

    def show_popup(self, message: str) -> None:
        """
        Displays a pop-up message in the center of the window with a black background
        for 5 seconds.

        :param message: The message to display in the pop-up
        :return: None
        """
        self.client.logger.debug(f"Function: show_popup. Message: {message}")
        self.popup_message = message
        self.popup_timer = pygame.time.get_ticks() + 3000  # Display for 3 seconds

    def display_popup(self, message: str) -> None:
        """
        Renders a popup message at the center of the GUI window.

        This function takes a message string, creates a text surface with it,
        and displays it within a black rectangular background in the center
        of the GUI window.

        :param message: The string to display in the popup message.
        :return: None
        """
        font = ui_font(24)
        text = font.render(message, True, (255, 255, 255))
        rect = text.get_rect(center=(self.window_width // 2, self.window_height // 2))
        pygame.draw.rect(self.window, (0, 0, 0), rect.inflate(20, 10))
        self.window.blit(text, rect)


if __name__ == "__main__":
    from hanabi.core.client_launcher import Client

    test_client = Client()
    gui = GUI(test_client)
    gui.run()
