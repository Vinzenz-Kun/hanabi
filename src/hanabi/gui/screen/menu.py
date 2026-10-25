import pygame  # type: ignore
from hanabi.gui import theme
from hanabi.gui.fonts import ui_font
from hanabi.gui.widgets.colors import Colors as colors


class MenuScreen:
    def __init__(self, gui) -> None:
        """
        Initializes the MenuScreen class with default settings.

        :param gui: The GUI instance to which this menu screen belongs.
        :type gui: hanabi.gui.gui_launcher.GUI
        """

        self.gui = gui
        self.font = ui_font(24)
        self.colors = {
            "black": pygame.Color(0, 0, 0),
            "white": pygame.Color(255, 255, 255),
            "blue": pygame.Color(0, 0, 255),
            "green": pygame.Color(0, 255, 0),
            "gray": pygame.Color(200, 200, 200),
        }
        self.create_ui_elements()

    def create_ui_elements(self) -> None:
        """
        Creates the UI elements for the menu screen, such as the server connect button, game connect button, lobby button, game button, and result button.

        :return: None
        """
        self.menu_buttons = {
            "server_connect": pygame.Rect(300, 140, 300, 48),
            "game_connect": pygame.Rect(300, 204, 300, 48),
            "lobby": pygame.Rect(300, 268, 300, 48),
            "game": pygame.Rect(300, 332, 300, 48),
            "result": pygame.Rect(300, 396, 300, 48),
        }

    def render(self) -> None:
        """
        Renders the menu screen with buttons for navigation to different screens.

        :return: None
        """
        theme.paint(self.gui.window)
        pygame.display.set_caption(self.gui.language_config.get_translation("menu"))
        title = ui_font(36).render(
            self.gui.language_config.get_translation("menu_title"),
            True,
            theme.GOLD,
        )
        self.gui.window.blit(
            title, (self.gui.window_width // 2 - title.get_width() // 2, 48)
        )

        for screen, rect in self.menu_buttons.items():
            theme.button(
                self.gui.window,
                rect,
                self.gui.language_config.get_translation(screen),
                self.font,
                "accent" if screen in self.gui.visited_screens else "quiet",
            )

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        """
        Handles user input in the menu screen.

        :param events: A list of pygame events to process.
        :return: None
        """
        for event in events:
            self.gui.handle_generic_input(event)

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                for screen, rect in self.menu_buttons.items():
                    if rect.collidepoint(mouse_pos):
                        if screen in self.gui.visited_screens:
                            self.transition_to_screen(screen)
                        else:
                            self.gui.client.logger.error(
                                f"(Menu) Cannot access {screen}: Screen not visited yet."
                            )

    def transition_to_screen(self, screen: str) -> None:
        """
        Transitions the GUI to the specified screen and updates the list of visited screens.

        :param screen: The target screen to transition to. Can be one of "server_connect",
                    "game_connect", or "lobby".
        :type screen: str
        :return: None
        """
        if screen == "server_connect":
            self.gui.visited_screens = ["server_connect"]
            self.gui.client.disconnect_from_server()  # Ensure server disconnection
        elif screen == "game_connect":
            self.gui.visited_screens = ["server_connect", "game_connect"]
        elif screen == "lobby":
            self.gui.visited_screens = ["server_connect", "game_connect", "lobby"]
        # elif screen == "game":
        #     self.gui.visited_screens = ["server_connect", "game_connect", "lobby", "game"]

        self.gui.current_screen = screen
