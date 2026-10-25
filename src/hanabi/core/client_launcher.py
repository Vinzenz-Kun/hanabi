# -*- coding: utf-8 -*-
"""
Client implementation for Hanabi game.

This script allows a user to connect to the server, interact with the GUI,
create or join games, and participate in gameplay.

It follows PEP 8 guidelines and is UTF-8 encoded.
"""
import importlib
import socket
from typing import Tuple
import threading
import sys
import json
import os
import hanabi.utils.lib as lib  # Import the dict_to_game function
import time


def _gui_module():
    import hanabi.gui.gui_launcher as gui

    return gui


def _set_game_screen_observing(value: bool) -> None:
    """Set GameScreen.observing only if the GUI is already imported.

    Tests construct Client without pygame. Importing the GUI here would fail
    GitHub Actions the same way a top-level gui import did.
    """
    for name in ("hanabi.gui.gui_launcher", "hanabi.gui.screen.game_screen"):
        module = sys.modules.get(name)
        if module is None:
            continue
        game_screen = getattr(module, "GameScreen", None)
        if game_screen is not None:
            game_screen.observing = value

# Get the absolute path to the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to config.json
CONFIG_FILE = os.path.join(BASE_DIR, "..", "utils", "config.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
    config = json.load(config_file)


class Client:
    """
    Represents the client application for the Hanabi game.
    Handles communication with the server and integrates with the GUI.
    """

    def __init__(self) -> None:
        """
        Initializes the client instance.
        Sets up networking details and GUI integration.

        :return: None.
        """
        self.logger = lib.setup_logger("client_logger", "client.log")
        self.username = ""  # Username of the client user. Still empty.
        self.host = config.get("client_host")  # Default host from config
        self.port = str(config.get("client_advised_port"))  # Default port from config
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Client socket
        self.connected = False  # Connection status
        self.gui = None  # GUI instance
        self.lobby = []  # Tracks the current lobby state
        self.game_state = None  # Stores the current game state
        self.game_id = None  # The ID of the game the client is participating in
        self.connection_error = None  # Stores error messages for failed connections
        self.status = None
        self.lobby_settings = {
            "game_id": None,
            "storm_tokens": 3,
            "num_players": 0,
            "hint_tokens": 8,
            "color_rush": False,
            "timer_active": False,
            "timer_seconds": 120,
        }  # Dictionary with lobby settings, defaults are set
        self.logger.info("client started \n")
        # self.log_messages = []  # Store log messages
        # self.log_scroll_offset = 0  # Scroll offset for the log

    def connect_to_server(self) -> None:
        """
        Connects the client to a server.
        If the client is already connected, it closes the existing connection before connecting again.

        :return: None.
        """
        self.logger.info("Function(client): connect_to_server")
        # Connect to the Hanabi server.
        if self.connected:
            self.logger.warning("Reconnecting: Closing existing connection.")
            self.disconnect_from_server()

        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            # Establish connection to the server
            self.logger.info(f"Connecting to {self.host}:{self.port}...")
            self.s.connect((self.host, int(self.port)))
            self.logger.info("Connection established.")

            # Notify the server of the client's username
            self.s.send(
                json.dumps(
                    {"type": "connect_to_server", "username": str(self.username)}
                ).encode("utf-8")
            )
            self.logger.info(
                "Username sent to server. Message: {'type': 'connect_to_server', 'username': '%s'}",
                self.username,
            )

            # Update connection status
            self.connected = True
            threading.Thread(target=self.receive_message, daemon=True).start()
            self.logger.info("Started message listener thread.")
        except socket.error as e:
            self.logger.error(f"Connection failed: {e}")
            self.connection_error = f"Connection failed: {e}"
            self.connected = False

    def disconnect_from_server(self) -> None:
        """
        Disconnects the client from the server. If the client is already disconnected, nothing happens.

        :return: None.
        """
        if self.connected:
            self.logger.info("Disconnecting from server...")
            self.send_message(
                {"type": "client_disconnected", "username": self.username}
            )
            self.s.close()
            self.connected = False

    def handle_disconnect(self) -> None:
        """
        Handles cleanup when disconnecting from the server.

        :return: None.
        """
        try:
            if self.gui.current_screen == "":
                self.send_message(
                    {"type": "client_disconnected", "username": self.username}
                )
                if self.connected:
                    self.send_message(
                        {"type": "client_disconnected", "username": self.username}
                    )
                    self.s.close()
            if self.gui.current_screen == "server_connect":
                self.send_message(
                    {"type": "client_disconnected", "username": self.username}
                )
        except Exception as e:
            self.logger.error(f"Error during disconnect: {e}")
        finally:
            self.connected = False
            self.game_state = None
            self.game_id = None
            self.lobby = []
            self.gui.current_screen = "server_connect"

    def receive_message(self) -> None:
        """Receives a JSON-encoded message from the server."""
        self.logger.debug("Function: receive_message")
        while self.connected:
            try:
                # Receive and decode server message, if connected
                data = self.s.recv(10240).decode("utf-8")
                if data:
                    # Handle server message, if received
                    self.logger.info(f"message received {data}\n")
                    response = json.loads(data)
                    self.handle_server_response(response)
            except Exception as e:
                # Handle errors during message reception
                self.logger.info(f"Error receiving message: {e}")
                self.connected = False
                self.connection_error = "Connection lost."

    def handle_server_response(self, response: dict) -> None:
        """
        Processes the server's response messages based on their type.

        :param response: The JSON-decoded response object from the server
        :return: None.
        """
        self.logger.debug("Function: handle_server_response")  # Debugging
        try:
            self.logger.info(f"Received data(client): {response}")
            message_type = response.get("type").lower()

            if message_type == "joined_server":
                # Handle "joined_server" message. Transitioning to game connect screen
                self.logger.info(f"Server message: {response.get('response')}")
                self.gui.visited_screens.append("game_connect")
                self.gui.current_screen = "game_connect"
                self.logger.info("connected to server\n")

            elif message_type == "lobby_created":
                # Handle "lobby_created" message. Transitioning to lobby screen as a host.
                self.game_id = response["game_id"]
                self.lobby_settings["game_id"] = self.game_id
                self.lobby.append(self.username)
                self.logger.debug(f"Current lobby state: {self.lobby}")
                self.gui.visited_screens.append("lobby")
                self.gui.current_screen = "lobby"
                self.status = "host"
                _set_game_screen_observing(False)
                self.logger.info(
                    f"Transitioned to lobby with Game ID: {self.game_id}\n"
                )

            elif message_type == "lobby_joined":
                # Handle "lobby_joined" message. Transitioning to lobby screen as a player or observer.
                if response.get("error"):
                    self.logger.error(
                        f"Error joining lobby: {response.get('response')}"
                    )
                else:
                    self.game_id = response["game_id"]
                    self.lobby = response.get("players")
                    self.logger.debug(f"Current lobby state: {self.lobby}")
                    self.logger.info(
                        f"Joined lobby {self.game_id} with players: {self.lobby}\n"
                    )
                    self.gui.visited_screens.append("lobby")
                    self.gui.current_screen = "lobby"

            elif message_type == "lobby_observing":
                if response.get("error"):
                    self.logger.error(
                        f"Error joining lobby: {response.get('response')}"
                    )
                else:
                    self.game_id = response["game_id"]
                    self.lobby = response.get("players")
                    self.logger.debug(f"Current lobby state: {self.lobby}")
                    self.logger.info(
                        f"Joined lobby {self.game_id} with players: {self.lobby}\n"
                    )
                    self.gui.visited_screens.append("lobby")
                    self.gui.current_screen = "lobby"
                    self.observing = True

            elif message_type == "player_join":
                self.lobby.append(response["username"])
                self.logger.info(
                    f"{response['username']} Joined lobby {self.game_id} with players: {self.lobby}\n"
                )
                self.gui.visited_screens.append("lobby")
                self.gui.current_screen = "lobby"

            elif message_type == "provide_gameids":
                self.gui.game_ids = response.get("game_ids")
                self.logger.info(f"Available games: {self.gui.game_ids}")
                self.logger.info("searching available games\n")

            elif message_type == "game_created":
                # Update game state and transition to the lobby
                self.game_id = response["game_id"]
                self.game_state = lib.dict_to_game(response.get("game_state"))
                self.logger.info(f"Game created with ID: {self.game_id}")
                self.gui.visited_screens.append("lobby")
                self.gui.current_screen = "lobby"
                self.status = "host"

            elif message_type == "game_started":
                self.lobby_settings["timer_active"] = response["timer_active"]
                self.lobby_settings["timer_seconds"] = response["timer_seconds"]
                self.gui.screens["game"].timer.time_limit = response["timer_seconds"]
                self.gui.screens["game"].timer.timer_active = response["timer_active"]
                self.game_id = response["game_id"]
                self.game_state = lib.dict_to_game(response["game_state"])
                # self.logger.debug(f"game_state: {self.game_state}")
                self.gui.visited_screens.append("game")
                self.gui.current_screen = "game"
                self.logger.info("game started\n")

            elif message_type == "sync_state":
                game_state = response.get("game_state")
                if game_state:
                    chat = game_state["log_message"]
                    self.gui.add_log_message(chat)
                    if len(chat) == 5:
                        self.gui.add_log_message(["", "", chat[4], ""])
                    self.update_local_game_state(game_state)
                    #    gui.GUI.add_log_message(move_log)
                    self.logger.info("Game state successfully updated.\n")
                else:
                    self.logger.error("Error: sync_state message missing game_state.")

            elif message_type == "log_message":
                self.logger.debug("log:", response)
                chat = response.get("message")
                self.gui.add_log_message(chat)

            elif message_type == "provide_players":
                self.lobby = response["players"]

            elif message_type == "player_disconnected":
                disconnected_player = response.get("username")
                game_id = response.get("game_id")

                # Remove from lobby
                if disconnected_player in self.lobby:
                    self.lobby.remove(disconnected_player)

                # Update GUI based on current screen
                if self.gui.current_screen == "lobby":
                    self.gui.add_log_message(
                        ["", f"{disconnected_player} has left the lobby", "", ""]
                    )

                elif self.gui.current_screen == "game":
                    self.gui.add_log_message(
                        ["", f"{disconnected_player} has disconnected", "", ""]
                    )
                    self.gui.current_screen = "lobby"

            elif message_type == "game_ended":
                self.logger.info("Game ended. Displaying results\n")
                self.gui.screens["result"].set_result_data(response)
                self.gui.current_screen = "result"

            elif message_type == "game_ended_due_to_disconnect":
                disconnected_player = response.get("disconnected_player")

                # Reset game state
                self.game_state = None
                self.game_id = None
                self.lobby = []

                # Update GUI
                self.gui.current_screen = "server_connect"
                if disconnected_player:
                    self.gui.add_log_message(
                        [
                            "Game ended because",
                            f"{disconnected_player}",
                            "disconnected",
                            "",
                        ]
                    )
                else:
                    self.gui.add_log_message(
                        ["Game ended due to player disconnect", "", "", ""]
                    )

            elif message_type == "return_to_lobby":
                self.logger.info(
                    "Received return_to_lobby message. Resetting game state and transitioning to lobby."
                )
                self.lobby_settings = {
                    "game_id": response["game_id"],
                    "storm_tokens": 3,
                    "num_players": 0,
                    "hint_tokens": 8,
                    "color_rush": False,
                    "timer_active": False,
                    "timer_seconds": 0,
                }
                self.game_state = None  # Clear the local game state
                self.gui.current_screen = "lobby"

            elif message_type == "info":
                self.logger.info("Server message:", response["response"])

            elif message_type == "error":
                self.logger.error("Server error:", response["response"])

            else:
                self.logger.error("unidentified response received\n")

        except Exception as e:
            self.logger.error(f"Error handling server response: {e}")

    def send_message(self, message: dict) -> None:
        """
        Sends a JSON-encoded message to the server.

        :param message: The message object to send in from of a dictionary
        :return: None.
        """
        self.logger.debug(f"Function: send_message. Message: {message}")  # Debugging
        try:
            self.s.sendall(json.dumps(message).encode("utf-8"))
            self.logger.info(f"Message {message} sent successfully\n")
        except Exception as e:
            self.logger.error(f"failed to send message{message} {e}\n")

    def get_players(self) -> None:
        """
        Sends a request to the server to get the list of players in the current game.

        :return: None.
        """
        self.logger.debug("Function: get_players")
        # Requests the list of players from the server.
        self.send_message({"type": "get_players", "game_id": self.game_id})

    def join_lobby(self, game_id: int) -> None:
        """
        Sends a request to join an existing game lobby.

        :param game_id: The ID of the game to join
        :return: None.
        """
        self.logger.debug(f"Function: join_lobby {game_id}\n")
        _set_game_screen_observing(False)
        self.send_message(
            {"type": "join_lobby", "game_id": game_id, "username": self.username}
        )

    def observe_lobby(self, game_id: int) -> None:
        """
        Sends a request to the server to observe an existing game lobby.

        :param game_id: The ID of the game to observe
        :return: None.
        """
        self.logger.debug(f"Function: observe_lobby {game_id}\n")
        _set_game_screen_observing(True)
        self.send_message(
            {"type": "observe_lobby", "game_id": game_id, "username": self.username}
        )

    def finalize_lobby(self) -> None:
        """Sends a request to finalize the lobby and start the game with the preferred settings.

        :return: None.
        """
        self.logger.info("Function: finalize_lobby (client)\n")
        if self.game_state == None:
            self.send_message(
                {
                    "type": "finalize_lobby",
                    "game_id": self.game_id,
                    "settings": self.lobby_settings,
                }
            )
        else:
            self.send_message(
                {
                    "type": "finalize_lobby",
                    "game_id": self.game_id,
                    "settings": self.lobby_settings,
                    "game_state": self.game_state,
                }
            )

    def join_game(self, game_id: int) -> None:
        """
        Sends a request to the server to join an existing game.

        :param game_id: The ID of the game to join
        :return: None.
        """
        self.logger.debug("Function: join_game()")
        self.send_message({"type": "join_game", "game_id": game_id})

    def update_local_game_state(self, new_game_state: dict) -> None:
        """
        Updates the local game state with the new state received from the server.

        :param new_game_state: The new game state in form of a dictionary
        :return: None.
        """
        self.logger.info("trying to update game state\n")
        try:
            self.game_state = lib.dict_to_game(new_game_state)
            self.logger.info(f"Game state updated: {self.game_state}")
            self.logger.info("game state updated\n")
        except Exception as e:
            self.logger.error(f"Error updating local game state: {e}")
            self.logger.error("failed to update game state\n")

    def update_game_state(self) -> None:
        """
        Sends the current local game state to the server for synchronization with all players.
        This is called automatically after each gameplay action.

        :return: None.
        """
        self.logger.debug(
            f"Function (client): update_game_state for game {self.game_id}"
        )

        self.send_message(
            {
                "type": "game_state_update",
                "game_id": self.game_id,
                "game_state": lib.class_to_dict(self.game_state),
            }
        )

    # Gameplay actions
    def play_card(self, card_index: int) -> None:
        """
        Sends a request to play a card.

        :param card_index: Index of the card in the player's hand to play
        :return: None.
        """
        self.logger.info(f"Playing card at index {card_index}.")
        self.logger.info("trying to play a card\n")
        self.send_message(
            {"type": "play_card", "game_id": self.game_id, "card_index": card_index}
        )

    def discard_card(self, card_index: int) -> None:
        """
        Sends a request to discard a card.

        :param card_index: Index of the card in the player's hand to discard
        :return: None.
        """
        self.logger.info(f"Discarding card at index {card_index}.")
        self.logger.info("trying to discard a card\n")
        self.send_message(
            {"type": "discard_card", "game_id": self.game_id, "card_index": card_index}
        )

    def give_hint(self, target_player: str, hint_type: str, hint_value: str) -> None:
        """
        Sends a request to give a hint to another player.

        :param target_player: Username of the player receiving the hint
        :param hint_type: Type of hint ('color' or 'value')
        :param hint_value: The value of the hint (e.g., 'Red' or '2')
        :return: None.
        """
        self.logger.info(f"Giving a hint to {target_player}: {hint_type} {hint_value}.")
        self.logger.info("trying to give hint\n")
        self.send_message(
            {
                "type": "give_hint",
                "game_id": self.game_id,
                "target_player": target_player,
                "hint_type": hint_type,
                "hint_value": hint_value,
            }
        )

    def render_gui(self) -> None:
        """
        Initializes and runs the graphical user interface.

        :return: None.
        """
        self.logger.info("updating gui\n")
        self.gui = _gui_module().GUI(self)
        self.gui.run()


if __name__ == "__main__":
    # Create a client instance and run the GUI
    client = Client()
    client.render_gui()
