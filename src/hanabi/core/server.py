# -*- coding: utf-8 -*-
"""
Server implementation for Hanabi game.
Handles client connections, game creation, lobby management, and communication.
"""
import importlib
import socket
import threading
import json
import random
import os
import sys
import hanabi.utils.lib as lib
from hanabi.core.game import Game

# Get the absolute path to the directory containing this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Construct the full path to config.json
CONFIG_FILE = os.path.join(BASE_DIR, "..", "utils", "config.json")

with open(CONFIG_FILE, "r", encoding="utf-8") as config_file:
    config = json.load(config_file)

server_host = config.get("server_host")
server_port = int(config.get("server_advised_port"))

server_logger = lib.setup_logger("server_logger", "server.log")


class Server:
    """
    Represents the server application for the Hanabi Game.
    Handles the communication of the clients with eatch other.
    """

    def __init__(self) -> None:
        """
        Initializes the server instance.

        :return: None.
        """
        # List to store active client connections and game instances
        self.server_clients = (
            {}
        )  # Active client connections.    Key: username,  item: client_socket
        self.games = (
            {}
        )  # Active games dictionary.      Key: game_id,   item: game object (game object has list of usernames)
        self.obgames = {}
        self.lobbies = (
            {}
        )  # Active lobbies.               Key: game_id,   item: list[usernames]
        self.oblobbies = {}

        self.shutdown_event = threading.Event()  # Event to signal server shutdown

    # Function to start the server
    def start_server(self, host=server_host, port=server_port) -> None:
        """
        Starts the server, binding it to the given host and port.

        Listens for incoming connections and starts a new thread to handle each client.

        If the server is interrupted through typing shutdown in the console the shutdown is handled gracefully.

        :param host: The host to bind the server to. Defaults to the value of server_host fetched from the config.json.
        :param port: The port to bind the server to. Defaults to the value of server_port fetched from the config.json.
        :return: None
        """
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(10)
        server_logger.info(
            f"(in server.start_server) Server listening on {host}:{port}"
        )

        # Start console listener thread
        threading.Thread(target=self.console_input_listener, daemon=True).start()

        try:
            server_logger.info("Type shutdown to interrupt the server\n")
            while not self.shutdown_event.is_set():
                server_socket.settimeout(
                    1.0
                )  # Allows graceful exit when shutdown_event is set
                try:
                    # Start a new thread to handle the client
                    client_socket, client_address = server_socket.accept()
                    client_thread = threading.Thread(
                        target=self.handle_client, args=(client_socket, client_address)
                    )
                    client_thread.start()
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            server_logger.info("Keyboard interrupt received. Shutting down server...\n")
        finally:
            # Disconnect all clients

            server_logger.info("Closing all connections...\n")
            for username, client_socket in list(self.server_clients.items()):
                self.handle_client_disconnect(username, client_socket)
            server_socket.close()
            server_logger.info("Server shut down successfully.\n")

    def handle_client(
        self, client_socket: socket.socket, client_address: tuple
    ) -> None:
        """
        Handles communication with a single client.

        :return: None.
        """
        username = None
        try:
            server_logger.info(f"New connection from {client_address}\n")
            client_socket.send(
                json.dumps(
                    {
                        "type": "joined_server",
                        "response": "Welcome to the Hanabi Game Server!",
                    }
                ).encode("utf-8")
            )

            data = json.loads(client_socket.recv(10240).decode("utf-8").strip())
            username = data.get("username")
            if not username or username in self.server_clients:
                client_socket.send(
                    json.dumps(
                        {"type": "error", "response": "Invalid or duplicate username"}
                    ).encode("utf-8")
                )
                return

            # Register client
            self.server_clients[username] = client_socket
            server_logger.info(
                f"New client connected: {username} from {client_address}\n"
            )

            while True:
                try:
                    if not data:  # Client closed connection
                        raise ConnectionResetError("Client closed connection")

                    message = json.loads(
                        client_socket.recv(10240).decode("utf-8").strip()
                    )
                    message_type = message.get("type", "").lower()

                    if message_type == "exit":
                        server_logger.info(f"Client {client_address} disconnected.\n")
                        break

                    elif message_type == "create_lobby":
                        # Handles the request to create a new lobby
                        server_logger.info(
                            f"Created lobby by {message['host_username']}\n"
                        )
                        game_id = self.create_lobby(username)
                        client_socket.send(
                            json.dumps(
                                {"type": "lobby_created", "game_id": game_id}
                            ).encode("utf-8")
                        )

                    elif message_type == "join_lobby":
                        # Handles the request to join a lobby as a player
                        server_logger.info(
                            f"User {username} joined lobby {message['game_id']}\n"
                        )
                        game_id = message["game_id"]
                        response = self.join_lobby(username, game_id)
                        self.broadcast(game_id, response, client_socket)
                        client_socket.send(json.dumps(response).encode("utf-8"))

                    elif message_type == "observe_lobby":
                        # Handles the request to join a lobby as a observer
                        server_logger.info(
                            f"User {username} observing lobby {message['game_id']}\n"
                        )
                        game_id = message["game_id"]
                        response = self.observe_lobby(username, game_id)
                        self.broadcast(game_id, response, client_socket)
                        client_socket.send(json.dumps(response).encode("utf-8"))

                    elif message_type == "game_state_update":
                        # Handles the request to update the game state
                        game_id = message.get("game_id")
                        if game_id not in self.games:
                            server_logger.info(
                                f"(in server.handle_client: game_state_update) Error: Game {game_id} not found. Cannot update game state.\n"
                            )
                            return
                        game_state = message["game_state"]
                        self.games[game_id] = lib.dict_to_game(
                            message["game_state"]
                        )  # Update server's game state
                        # response = {"type": "sync_state", "game_state": message["game_state"]}
                        # self.broadcast(game_id, response, client_socket)
                        self.sync_game_state(game_id, game_state)
                        server_logger.info(
                            f"(in server.handle_client: game_state_update) Broadcasted game state for game {game_id}\n"
                        )

                    elif message_type == "finalize_lobby":
                        # Handles the request to finalize a lobby
                        server_logger.info("Message received: finalize lobby\n")
                        game_id = message["game_id"]
                        settings = message.get("settings")
                        game_state = message.get("game_state")
                        if 6 > len(self.lobbies[game_id]) > 1:
                            self.finalize_lobby(game_id, settings, game_state)

                    elif message_type == "game_ended":
                        # Handles the message that a game has ended
                        game_id = message["game_id"]
                        self.broadcast(game_id, {"type": "game_ended", **message})
                        server_logger.info(
                            f"Broadcasted game ended message for game {game_id}\n"
                        )

                    elif message_type == "return_to_lobby":
                        # handles the request to return to the lobby
                        game_id = message["game_id"]
                        if game_id in self.games:
                            # Notify all players and clean up the game
                            self.broadcast(
                                game_id, {"type": "return_to_lobby", "game_id": game_id}
                            )
                            self.lobbies[game_id] = message["players"]
                            self.games[game_id].reset()
                            server_logger.info(
                                f"Reset game and lobby for game ID: {game_id}\n"
                            )
                        else:
                            server_logger.error(
                                f"Invalid game_id in return_to_lobby message: {game_id}"
                            )

                    elif message_type == "connect_to_server":
                        # Handles the request to connect to the server
                        self.server_clients.append(client_socket)
                        client_socket.send(
                            json.dumps(
                                {
                                    "type": "joined_server",
                                    "response": f"Client {message['new_client'].get('username')} joined the server at {message['new_client'].server_host}:{message['new_client'].port}",
                                }
                            ).encode("utf-8")
                        )

                    elif message_type == "get_games":
                        # Handles the request to get the list of games. Important for the server connect screen
                        games_gameids = list(self.games.keys())
                        server_logger.info(f"Message: get_games. {games_gameids}\n")
                        client_socket.send(
                            json.dumps(
                                {
                                    "type": "provide_gameids",
                                    "response": "Active games, joinable through the given Game IDs",
                                    "game_ids": games_gameids,
                                }
                            ).encode("utf-8")
                        )

                    elif message_type == "get_players":
                        # Handles the request to get the list of players
                        player_names = self.lobbies[message["game_id"]]
                        client_socket.send(
                            json.dumps(
                                {
                                    "type": "provide_players",
                                    "response": f"Providing of players: {player_names}",
                                    "players": player_names,
                                }
                            ).encode("utf-8")
                        )

                    elif message_type == "client_disconnected":
                        # Handles the client disconnect
                        self.handle_client_disconnect(username, client_socket)

                    else:
                        client_socket.send(
                            json.dumps(
                                {
                                    "type": "error",
                                    "response": f"Invalid command.{message}",
                                }
                            ).encode("utf-8")
                        )
                except json.JSONDecodeError as e:
                    server_logger.error(f"Invalid message format from {username}: {e}")
                    continue
                except (ConnectionResetError, socket.error) as e:
                    server_logger.info(f"Client {username} connection lost: {e}")
                    break
        # except (json.JSONDecodeError, ConnectionResetError) as e:
        # server_logger.error(f"Error with client communitcation {client_address}: {e}\n")
        # self.disconnect_client(username, client_socket)
        except Exception as e:
            server_logger.error(f"Error with client {client_address}: {e}\n")
            # self.disconnect_client(username, client_socket)
        finally:
            if username:
                self.handle_client_disconnect(username, client_socket)
            # self.disconnect_client(username, client_socket)
            # client_socket.close()

    def disconnect_client(
        self, username: str, client_socket: socket.socket
    ) -> None:  # Unused
        """
        Handles cleanup when a client disconnects.

        :param username: The username of the disconnected client.
        :param client_socket: The socket of the disconnected client.
        :return: None
        """
        if username in self.server_clients:
            del self.server_clients[username]

        # Remove the player from any lobby
        for game_id, players in self.lobbies.items():
            if username in players:
                players.remove(username)
                if (
                    not players or players[0] == username
                ):  # If the lobby is empty, delete it
                    del self.lobbies[game_id]
                    server_logger.debug(
                        f"(server.disconnect_client) Lobby {game_id} deleted from lobbies.\n"
                    )
                    del self.games[game_id]
                    server_logger.debug(
                        f"(server.disconnect_client) Game {game_id} deleted from games.\n"
                    )
                    self.broadcast(
                        game_id,
                        {"type": "game_ended_due_to_disconnect", "game_id": game_id},
                        client_socket,
                    )
                    server_logger.info(f"(server.disconnect_client) Lobby {game_id}\n")

        try:
            client_socket.close()
            server_logger.info(
                f"(in server.disconnect_client) Client {username} disconnected.\n"
            )
        except Exception as e:
            server_logger.error(f"Error closing client socket: {e}\n")

    def handle_client_disconnect(
        self, username: str, client_socket: socket.socket
    ) -> None:
        """
        Enhanced disconnect handling with cleanup and notifications

        :param username: The username of the disconnected client.
        :param client_socket: The socket of the disconnected client.
        :return: None
        """
        try:
            if username in self.server_clients:
                # Find all games/lobbies the user is in
                affected_games = []
                for game_id, players in self.lobbies.items():
                    if username in players:
                        affected_games.append(game_id)
                        players.remove(username)

                        # Notify other players in the lobby
                        disconnect_message = {
                            "type": "player_disconnected",
                            "username": username,
                            "game_id": game_id,
                        }

                        # If lobby becomes empty or host leaves, end the game
                        if not players or players[0] == username:
                            del self.lobbies[game_id]
                            if game_id in self.games:
                                del self.games[game_id]

                            disconnect_message["type"] = "game_ended_due_to_disconnect"

                        self.broadcast(game_id, disconnect_message, client_socket)

                # Remove from active clients
                del self.server_clients[username]

                for game_id, observers in list(self.oblobbies.items()):
                    if username in observers:
                        observers.remove(username)
                        if game_id in self.obgames:
                            self.obgames[game_id] = [
                                obs for obs in self.obgames[game_id] if obs != username
                            ]

                server_logger.info(
                    f"Client {username} disconnected and cleaned up from {len(affected_games)} games"
                )

        except Exception as e:
            server_logger.error(f"Error during client disconnect cleanup: {e}")
        finally:
            try:
                client_socket.close()
            except:
                pass

    def create_lobby(self, host_username: str) -> int:
        """
        Creates a new lobby with a unique game_id.

        :param host_username: The username of the host of the new lobby.
        :return: The game_id of the newly created lobby.
        """
        while True:
            game_id = random.randint(000000, 999999)
            if game_id not in self.games:
                self.games[game_id] = None  # Placeholder until finalized
                self.lobbies[game_id] = [host_username]
                self.obgames[game_id] = None
                self.oblobbies[game_id] = []
                return game_id

    def join_lobby(self, username: str, game_id: int) -> dict:
        """
        Adds a user to a lobby if it exists and is not yet finalized.

        :param username: The username of the user joining the lobby.
        :param game_id: The game_id of the lobby to join.
        :return: A dictionary containing the response type and response message.
        """
        if game_id not in self.lobbies:
            return {"type": "error", "response": "Lobby not found"}
        if self.games[game_id] is not None:
            return {"type": "error", "response": "Game already started"}
        if username in self.lobbies[game_id]:
            return {"type": "error", "response": "User already in the lobby"}
        self.lobbies[game_id].append(username)
        for player in self.lobbies[game_id]:
            try:
                self.server_clients[player].sendall(
                    json.dumps(
                        {
                            "type": "player_join",
                            "username": username,
                            "game_id": game_id,
                        }
                    ).encode("utf-8")
                )
            except Exception as e:
                server_logger.error(f"Error sending message to client: {e}\n")
        return {
            "type": "lobby_joined",
            "game_id": game_id,
            "players": self.lobbies[game_id],
            "username": username,
        }

    def observe_lobby(self, username: str, game_id: int) -> dict:
        """
        Adds a user to a lobby if it exists and is not yet finalized.

        :param username: The username of the user joining the lobby.
        :param game_id: The game_id of the lobby to join.
        :return: A dictionary containing the response type and response message.
        """
        if game_id not in self.lobbies:
            return {"type": "error", "response": "Lobby not found"}
        if self.games[game_id] is not None:
            return {"type": "error", "response": "Game already started"}
        if username in self.lobbies[game_id]:
            return {"type": "error", "response": "User already in the lobby"}
        self.oblobbies[game_id].append(username)
        return {
            "type": "lobby_observing",
            "game_id": game_id,
            "players": self.lobbies[game_id],
            "username": username,
        }

    def finalize_lobby(self, game_id: int, settings: dict, game_state=None) -> None:
        """
        Finalizes a lobby, initializes the game, and notifies players.

        :param game_id: The game_id of the lobby to finalize.
        :param settings: A dictionary containing the game settings such as number of players, hint tokens, storm tokens, and timer settings.
        :param game_state: An optional dictionary containing the game state to load the game from.
        :return: None
        """
        if game_id not in self.lobbies:
            return
        player_names = self.lobbies.pop(game_id, [])
        self.obgames[game_id] = self.oblobbies.pop(game_id, [])
        host_username = player_names[0]
        server_logger.debug(f"Set Host username: {host_username}")
        host_socket = self.server_clients[host_username]
        server_logger.debug(f"set host socket to: {host_socket}")
        num_players = len(player_names)
        timer_active = settings.get("timer_active")
        timer_seconds = settings.get("timer_seconds")

        if game_state is None:
            # If there is no game state, create a new game
            server_logger.debug(f"Set number of players to: {num_players}")
            storm_tokens = settings.get("storm_tokens")
            server_logger.debug(f"Set storm tokens to: {storm_tokens}")
            hint_tokens = settings.get("hint_tokens")
            server_logger.debug(f"Set hint tokens to: {hint_tokens}")
            color_rush = settings.get("color_rush")
            server_logger.debug(f"Set color rush to: {color_rush}")

            game = Game(
                game_id,
                num_players,
                player_names,
                hint_tokens,
                storm_tokens,
                color_rush,
            )
        else:
            # If there is a game state, load the game from it
            game = lib.dict_to_game(game_state)
            server_logger.debug(f"(with game_state)Game: {game}\n")

        # Notify all players
        self.games[game_id] = game
        server_logger.info(
            f"Game initialized with following parameters: {game_id, num_players, player_names, game.hint_token, game.storm_token, game.color_rush}\n"
        )
        self.broadcast(
            game_id,
            {
                "type": "game_started",
                "game_id": game_id,
                "players": player_names,
                "game_state": lib.class_to_dict(game),
                "timer_active": timer_active,
                "timer_seconds": timer_seconds,
            },
            host_socket,
        )

    def broadcast(self, game_id: int, message: dict, sender_socket=None) -> None:
        """
        Sends a message to all clients in a specific game.
        If a game_state exists, synchronize it after broadcasting.

        :param game_id: The game_id of the game to broadcast the message to.
        :param message: The message to broadcast.
        :return: None
        """
        server_logger.info("Trying to broadcast to all player\n")
        if game_id in self.games and self.games[game_id]:
            for player in self.games[game_id].players:
                try:
                    server_logger.info(f"Sending message {message} to {player.name}\n")
                    self.server_clients[player.name].sendall(
                        json.dumps(message).encode("utf-8")
                    )
                except Exception as e:
                    server_logger.error(f"Error sending message to client: {e}\n")
            for observer in self.obgames[game_id]:
                try:
                    server_logger.info(f"Sending message {message} to {observer}\n")
                    self.server_clients[observer].sendall(
                        json.dumps(message).encode("utf-8")
                    )
                except Exception as e:
                    server_logger.error(f"Error sending message to client: {e}\n")
        else:
            server_logger.error(f"Game {game_id} not found. Message not broadcast.\n")

    def sync_game_state(self, game_id: int, game_state: dict) -> None:
        """
        Sends the updated game state to all players in the game.

        :param game_id: The game_id of the game to sync the state of.
        :param game_state: The game state to sync.
        :return: None
        """

        if game_id not in self.games:
            server_logger.error(
                f"(in sync_game_state) Error: Game {game_id} not found. Cannot sync state.\n"
            )
            return

        game = self.games.get(game_id)
        self.broadcast(game_id, {"type": "sync_state", "game_state": game_state})
        server_logger.info(
            f"(sync_game_state) Broadcasted updated game state for game {game_id}\n"
        )

    def console_input_listener(self) -> None:
        """
        Listens for console input to shut down the server.

        :return: None
        """
        while not self.shutdown_event.is_set():
            try:
                command = input()
            except EOFError:
                return
            if command.lower() == "shutdown":
                server_logger.info("Shutdown command received. Closing server...\n")
                self.shutdown_event.set()


# Run the server
if __name__ == "__main__":
    server = Server()
    server.start_server()
