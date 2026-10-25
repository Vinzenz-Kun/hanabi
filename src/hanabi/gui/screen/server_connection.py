from hanabi.gui.widgets.cardselection import CardSelection
import pygame
from hanabi.gui import theme
from hanabi.gui.fonts import ui_font  # type: ignore
from hanabi.gui.widgets.colors import Colors as colors


class ServerConnectScreen:
    def __init__(self, gui) -> None:
        """
        Initializes the ServerConnectScreen class with default settings and links it to the client.

        :param gui: The parent GUI instance.
        :type gui: hanabi.gui.gui_launcher.GUI
        :return: None
        """
        self.gui = gui
        self.client = gui.client
        self.font = ui_font(20)
        self.colors = {
            "black": colors.black,
            "white": colors.white,
            "blue": colors.blue,
            "green": colors.green,
            "gray": colors.gray,
            "red": colors.red,
        }
        self.input_active = {"host": False, "port": False, "username": False}
        self.error_type = None
        self.create_input_boxes()

    def create_input_boxes(self) -> None:
        """
        Creates the input boxes for the host, port and username, as well as the connect button.

        :return: None
        """
        self.host_input_box = pygame.Rect(390, 230, 260, 40)
        self.port_input_box = pygame.Rect(390, 290, 260, 40)
        self.username_input_box = pygame.Rect(390, 350, 260, 40)
        self.connect_button = pygame.Rect(390, 420, 260, 44)

    def render(self) -> None:
        """
        Renders the server connection screen with input fields for host, port and username, a connect button and displays an error message if any.

        :return: None
        """
        # Clear the screen and set the caption
        theme.paint(self.gui.window)
        pygame.display.set_caption(
            self.gui.language_config.get_translation("connection_details")
        )
        theme.panel(self.gui.window, pygame.Rect(180, 150, 540, 360))
        title = ui_font(36).render(
            self.gui.language_config.get_translation("hanabi_connection"),
            True,
            theme.GOLD,
        )
        self.gui.window.blit(
            title, (self.gui.window_width // 2 - title.get_width() // 2, 80)
        )

        # Draw the input fields and labels
        self._draw_input_field(
            self.gui.language_config.get_translation("Host"),
            self.host_input_box,
            self.client.host,
            self.input_active["host"],
        )
        self._draw_input_field(
            self.gui.language_config.get_translation("Port"),
            self.port_input_box,
            str(self.client.port),
            self.input_active["port"],
        )
        self._draw_input_field(
            self.gui.language_config.get_translation("username"),
            self.username_input_box,
            self.client.username,
            self.input_active["username"],
        )

        # Draw the connect button
        theme.button(
            self.gui.window,
            self.connect_button,
            self.gui.language_config.get_translation("connect"),
            self.font,
        )
        if self.error_type:
            theme.text(
                self.gui.window,
                self.get_error_message(),
                self.font,
                (200, 540),
                theme.DANGER,
            )

    def _draw_input_field(
        self, label: str, input_box: pygame.Rect, value: str, active: bool
    ) -> None:
        """
        Draws an input field to the screen with a given label and value, highlighting the field if active.

        :param label: The label of the input field
        :param input_box: The bounding box of the input field
        :param value: The current value of the input field
        :param active: Whether the input field is currently active
        :return: None
        """
        theme.text(self.gui.window, label, self.font, (input_box.x - 150, input_box.y + 8), theme.MUTED)
        theme.field(self.gui.window, input_box, value, self.font, active)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        """
        Handles input events for the server connection screen.

        Processes mouse button down events to detect clicks on the connect button
        or the input boxes for host, port, and username, activating the appropriate
        input field. Processes key down events to handle text input for the active
        input field.

        :param events: A list of pygame events to process.
        :return: None
        """
        for event in events:
            self.gui.handle_generic_input(event)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.connect_button.collidepoint(event.pos):
                    self.try_connect()
                elif self.host_input_box.collidepoint(event.pos):
                    self._set_active_input("host")
                elif self.port_input_box.collidepoint(event.pos):
                    self._set_active_input("port")
                elif self.username_input_box.collidepoint(event.pos):
                    self._set_active_input("username")
                else:
                    self._set_active_input(None)
            elif event.type == pygame.KEYDOWN:
                # self.gui.handle_generic_input(event)
                self._handle_text_input(event)

    def _set_active_input(self, field: str) -> None:
        """
        Sets the active input field for the server connection screen.

        :param field: The name of the input field to activate.
        :return: None
        """
        self.input_active = {"host": False, "port": False, "username": False}
        if field:
            self.input_active[field] = True

    def _handle_text_input(self, event: pygame.event.Event) -> None:
        """
        Handles text input events for the server connection screen.

        Processes key down events to handle text input for the active input field.
        Deletes characters when the backspace key is pressed, connects to the server
        when the return key is pressed, and adds characters to the input field when
        alphanumeric keys are pressed. If the shift key is pressed, it does nothing.
        If any other key is pressed, it shows an error popup.

        :param event: A pygame event to process.
        :return: None
        """
        if event.key == pygame.K_BACKSPACE:
            if self.input_active["host"]:
                self.client.host = self.client.host[:-1]
            elif self.input_active["port"]:
                self.client.port = self.client.port[:-1]
            elif self.input_active["username"]:
                self.client.username = self.client.username[:-1]
        elif event.key == pygame.K_RETURN:
            if self.input_active["username"]:
                self.try_connect()
        else:
            if self.input_active["host"]:
                if event.unicode.isalnum() or event.unicode == ".":
                    self.client.host += event.unicode
                else:
                    self.gui.show_popup(
                        f"{self.gui.language_config.get_translation('invalid_character_host')}"
                    )
            elif self.input_active["port"]:
                if event.unicode.isdigit() and len(self.client.port) < 5:
                    self.client.port += event.unicode
                else:
                    self.gui.show_popup(
                        f"{self.gui.language_config.get_translation('invalid_character_port')}"
                    )
            elif self.input_active["username"]:
                if event.unicode.isalnum():
                    self.client.username += event.unicode
                elif event.key == (pygame.K_LSHIFT or pygame.K_RSHIFT):
                    pass
                else:
                    self.gui.show_popup(
                        f"{self.gui.language_config.get_translation('invalid_character')}"
                    )

    def try_connect(self) -> None:
        """
        Attempts to connect to the server and handle connection status.

        :return: None
        """

        if not self.client.username.strip():
            self.error_type = "username_empty"
            return
        try:
            port = int(self.client.port)
        except ValueError:
            self.error_type = "port_type_error"
            return
        if not 1024 <= port <= 65535:
            self.error_type = "port_range_error"
            return
        else:
            self.error_type = None
            self.client.connect_to_server()
            if self.client.connected:
                self.gui.current_screen = "lobby"
            else:
                self.error_type = "connection_failed"

    def get_error_message(self) -> str:
        """
        Returns the error message for the current error type as a string.

        Returns an empty string if there is no error.

        :return: str
        """
        messages = {
            "port_type_error": self.gui.language_config.get_translation("port_type_error"),
            "username_empty": self.gui.language_config.get_translation("username_empty"),
            "port_range_error": self.gui.language_config.get_translation("port_range_error"),
            "connection_failed": self.gui.language_config.get_translation("connection_failed"),
        }
        return messages.get(self.error_type, "")
