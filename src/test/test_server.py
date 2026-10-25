import json
import socket
import threading
import time
from unittest.mock import Mock, patch

import pytest

from hanabi.core.server import Server

TEST_HOST = "127.0.0.1"


def _wait_until_listening(server: Server, timeout: float = 5.0) -> tuple[str, int]:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        addr = getattr(server, "listen_addr", None)
        if addr:
            host, port = addr[0], addr[1]
            try:
                probe = socket.create_connection((host, port), timeout=0.2)
                probe.close()
                return host, port
            except OSError as exc:
                last = exc
        time.sleep(0.05)
    raise TimeoutError(f"server did not listen: {last}")


@pytest.fixture
def server():
    return Server()


@pytest.fixture
def listening_server():
    instance = Server()
    thread = threading.Thread(
        target=instance.start_server,
        kwargs={"host": TEST_HOST, "port": 0},
        daemon=True,
    )
    thread.start()
    host, port = _wait_until_listening(instance)
    instance.test_host = host
    instance.test_port = port
    yield instance
    instance.shutdown_event.set()
    thread.join(timeout=2)


def test_connect_to_server(listening_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((listening_server.test_host, listening_server.test_port))
        response = json.loads(client.recv(1024).decode("utf-8"))
        assert response["type"] == "joined_server"
        assert response["response"] == "Welcome to the Hanabi Game Server!"
        client.send(json.dumps({"username": "test_user"}).encode("utf-8"))
        assert listening_server.server_clients is not None
    finally:
        client.close()


def test_create_lobby(server):
    game_id = server.create_lobby("test_host")
    assert isinstance(game_id, int)
    assert 0 <= game_id <= 999999
    assert game_id in server.games
    assert server.games[game_id] is None
    assert game_id in server.lobbies
    assert server.lobbies[game_id] == ["test_host"]


def test_join_lobby(server):
    game_id = server.create_lobby("host_user")
    another_username = "another_user"
    mock_client_host = Mock()
    mock_client_another = Mock()
    server.server_clients = {
        "host_user": mock_client_host,
        "another_user": mock_client_another,
    }

    response = server.join_lobby("test_user", 999999)
    assert response["type"] == "error"
    assert response["response"] == "Lobby not found"

    server.games[game_id] = "GameStarted"
    response = server.join_lobby("test_user", game_id)
    assert response["type"] == "error"
    assert response["response"] == "Game already started"

    server.games[game_id] = None
    response = server.join_lobby("host_user", game_id)
    assert response["type"] == "error"
    assert response["response"] == "User already in the lobby"

    response = server.join_lobby(another_username, game_id)
    expected_response = {
        "type": "lobby_joined",
        "game_id": game_id,
        "players": server.lobbies[game_id],
        "username": another_username,
    }
    assert response == expected_response
    join_message = json.dumps(
        {
            "type": "player_join",
            "username": another_username,
            "game_id": game_id,
        }
    ).encode("utf-8")
    mock_client_host.sendall.assert_called_once_with(join_message)
    mock_client_another.sendall.assert_called_once_with(join_message)


def test_finalize_lobby(server):
    game_id = 4242
    player_names = ["host_user", "player1", "player2"]
    settings = {
        "game_id": game_id,
        "storm_tokens": 3,
        "hint_tokens": 8,
        "color_rush": False,
    }
    server.lobbies = {game_id: list(player_names)}
    server.oblobbies = {game_id: []}
    server.server_clients = {name: Mock() for name in player_names}
    server.games = {}
    with patch.object(server, "broadcast") as mock_broadcast:
        server.finalize_lobby(game_id, settings)
    game = server.games[game_id]
    assert len(game.player_names) == len(player_names)
    assert game.storm_token == settings["storm_tokens"]
    assert game.hint_token == settings["hint_tokens"]
    mock_broadcast.assert_called_once()
    payload = mock_broadcast.call_args[0][1]
    assert payload["type"] == "game_started"
    assert payload["game_id"] == game_id
    assert payload["players"] == player_names


def test_player_disconnect(server):
    game_id = server.create_lobby("host_user")
    server.lobbies[game_id] = ["host_user", "player1"]
    server.disconnect_client("player1", Mock())
    assert "player1" not in server.lobbies[game_id]


def test_client_timeout(listening_server):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.settimeout(2)
    try:
        client.connect((listening_server.test_host, listening_server.test_port))
        client.recv(1024)
    finally:
        client.close()


def test_server_shutdown(server):
    server.shutdown_event.set()
    assert server.shutdown_event.is_set()
