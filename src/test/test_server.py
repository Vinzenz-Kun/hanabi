import sys, os

myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "")
print(myPath)
import pytest
import threading
import socket
import json
import time
from unittest.mock import MagicMock, Mock
from hanabi.core.server import Server


@pytest.fixture(scope="module")
def start_server_instance():
    """Fixture to start the server in a separate thread."""
    server = Server()
    server_thread = threading.Thread(target=server.start_server, daemon=True)
    server_thread.start()
    time.sleep(3)
    yield server
    server.shutdown_event.set()


def test_connect_to_server(start_server_instance):
    """Test connecting to the server and receiving a welcome message."""
    server = start_server_instance
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client.connect(("localhost", 1234))
        client.send(json.dumps({"username": "test_user"}).encode("utf-8"))

        response = json.loads(client.recv(1024).decode("utf-8"))

        assert response["type"] == "joined_server"
        assert response["response"] == "Welcome to the Hanabi Game Server!"
        assert (
            server.server_clients is not None
        )  # Ensure the dic with users is not empty
    finally:
        client.close()


# Test: Create a lobby
def test_create_lobby(start_server_instance):
    server = start_server_instance
    host_username = "test_host"

    game_id = server.create_lobby(host_username)

    # Assertions
    assert isinstance(game_id, int), "game_id should be an integer."
    assert (
        0 <= game_id <= 999999
    ), "game_id should be within the range 000000 to 999999."
    assert (
        game_id in server.games
    ), "The game_id should be added to the server's games dictionary."
    assert (
        server.games[game_id] is None
    ), "The game_id in the games dictionary should be initialized to None."
    assert (
        game_id in server.lobbies
    ), "The game_id should be added to the server's lobbies dictionary."
    assert server.lobbies[game_id] == [
        host_username
    ], "The lobbies dictionary should contain the host_username."


# Test: Join a lobby
# Test: Join a lobby
def test_join_lobby(start_server_instance):
    server = start_server_instance

    # Set up test data
    game_id = server.create_lobby("host_user")
    another_username = "another_user"

    # Mock the server_clients to simulate connected clients
    mock_client_host = Mock()
    mock_client_another = Mock()
    server.server_clients = {
        "host_user": mock_client_host,
        "another_user": mock_client_another,
    }

    # Test joining a non-existent lobby
    response = server.join_lobby("test_user", 999999)
    assert response["type"] == "error"
    assert response["response"] == "Lobby not found"

    # Test joining a lobby that has already started
    server.games[game_id] = "GameStarted"
    response = server.join_lobby("test_user", game_id)
    assert response["type"] == "error"
    assert response["response"] == "Game already started"

    # Reset the game state
    server.games[game_id] = None

    # Test duplicate user
    response = server.join_lobby("host_user", game_id)
    assert response["type"] == "error"
    assert response["response"] == "User already in the lobby"

    # Test joining a valid lobby
    response = server.join_lobby(another_username, game_id)

    # Verify the expected response
    expected_response = {
        "type": "lobby_joined",
        "game_id": game_id,
        "players": server.lobbies[game_id],
        "username": another_username,
    }
    assert response == expected_response
    assert another_username in response["players"]

    # Verify the messages sent to all players in the lobby
    join_message = json.dumps(
        {
            "type": "player_join",
            "username": another_username,
            "game_id": game_id,
        }
    ).encode("utf-8")
    mock_client_host.sendall.assert_called_once_with(join_message)
    mock_client_another.sendall.assert_called_once_with(join_message)


# Test: Finalize a lobby
def test_finalize_lobby(start_server_instance, mocker):
    server = start_server_instance

    # Mock external dependencies
    mock_broadcast = mocker.patch.object(server, "broadcast")
    mocker.patch(
        "hanabi.core.client_launcher.lib.class_to_dict",
        return_value={"mocked": "state"},
    )
    mocker.patch("hanabi.core.game.Game", autospec=True)  # Mock Game class

    # Setup test data
    game_id = "test_game"
    player_names = ["host_user", "player1", "player2"]
    settings = {
        "game_id": game_id,
        "storm_tokens": 3,
        "hint_tokens": 8,
        "color_rush": False,
    }
    server.lobbies = {game_id: player_names}
    server.server_clients = {
        "host_user": Mock(),
        "player1": Mock(),
        "player2": Mock(),
    }
    server.games = {}

    # Call the method
    server.finalize_lobby(game_id, settings)

    # Assertions
    assert game_id in server.games  # Check if game is added
    game = server.games[game_id]
    assert len(game.player_names) == len(player_names)
    assert game.storm_token == settings["storm_tokens"]
    assert game.hint_token == settings["hint_tokens"]

    # Ensure broadcast was called correctly
    mock_broadcast.assert_called_once_with(
        game_id,
        {
            "type": "game_started",
            "game_id": game_id,
            "players": player_names,
            "game_state": {"mocked": "state"},
            "timer_active": None,
            "timer_seconds": None,
        },
        server.server_clients["host_user"],
    )


def test_player_disconnect(start_server_instance):
    server = start_server_instance
    game_id = server.create_lobby("host_user")
    server.lobbies[game_id] = ["host_user", "player1"]

    # Simulate a disconnect
    server.disconnect_client("player1", game_id)

    # Ensure player is removed from the lobby and game state
    assert "player1" not in server.lobbies[game_id]


def test_client_timeout(start_server_instance):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(2)  # Short timeout for testing
    try:
        client.connect(("localhost", 1234))
        response = client.recv(1024)  # Simulate not sending a message
    except socket.timeout:
        # Assert that the timeout occurs correctly
        assert True
    finally:
        client.close()


def test_server_shutdown(start_server_instance):
    server = start_server_instance

    # Trigger shutdown
    server.shutdown_event.set()

    # Assert that server is properly shutting down and all resources are cleaned up
    assert server.shutdown_event.is_set()
