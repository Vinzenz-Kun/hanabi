import sys, os

# Ensure the module’s directory is in the Python path.
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + "")
print("Test module path:", myPath)

import pytest
import socket
import json
from unittest.mock import Mock, patch

# Import the Client class.
from hanabi.core.client_launcher import Client


# =============================================================================
# Fixture
# =============================================================================
@pytest.fixture
def mock_client():
    """
    Create a new Client instance for each test with mocked logger and GUI.
    Also, override receive_message to a no-op to prevent background thread interference.
    """
    client = Client()
    client.username = "test_client"

    # Replace logger with a mock.
    client.logger = Mock()

    # Replace the GUI with a mock.
    client.gui = Mock()
    client.gui.visited_screens = []
    client.gui.current_screen = ""
    client.gui.add_log_message = Mock()

    # Set an initial game_id (if needed by tests).
    client.game_id = 111111

    # Prevent the background thread from interfering by patching receive_message.
    client.receive_message = lambda: None

    return client


# =============================================================================
# Test: connect_to_server (using patch on socket.socket)
# =============================================================================
@patch("socket.socket")
def test_connect_to_server(mock_socket_class, mock_client):
    """
    Test that connect_to_server establishes a connection, sends the correct
    JSON message, and sets connected True.
    """
    # Create a mock socket instance.
    mock_sock = Mock()
    mock_socket_class.return_value = mock_sock

    # Set expected host and port.
    mock_client.host = "localhost"
    mock_client.port = "8000"

    # Call connect_to_server.
    mock_client.connect_to_server()

    # Assert that connect() was called with the expected arguments.
    mock_sock.connect.assert_called_once_with(("localhost", 8000))

    # Assert that send() was called with a JSON-encoded "connect_to_server" message.
    mock_sock.send.assert_called_once()
    sent_data = mock_sock.send.call_args[0][0]
    sent_message = json.loads(sent_data.decode("utf-8"))
    assert sent_message["type"] == "connect_to_server"
    assert sent_message["username"] == mock_client.username

    # Verify that the client marks itself as connected.
    assert mock_client.connected is True


# =============================================================================
# Test: send_message sends JSON data correctly.
# =============================================================================
def test_send_message(mock_client):
    mock_sock = Mock()
    mock_client.s = mock_sock
    message = {"type": "test_message", "data": "hello"}

    mock_client.send_message(message)

    # Check that sendall was called with the proper JSON-encoded data.
    mock_sock.sendall.assert_called_once()
    sent_data = mock_sock.sendall.call_args[0][0]
    sent_message = json.loads(sent_data.decode("utf-8"))
    assert sent_message == message


# =============================================================================
# Test: get_players sends the correct message.
# =============================================================================
def test_get_players(mock_client):
    mock_client.send_message = Mock()
    mock_client.game_id = 333333
    mock_client.get_players()
    mock_client.send_message.assert_called_once_with(
        {"type": "get_players", "game_id": 333333}
    )


# =============================================================================
# Test: join_lobby sends the correct message.
# =============================================================================
def test_join_lobby(mock_client):
    mock_client.send_message = Mock()
    mock_client.username = "test_client"
    mock_client.join_lobby(444444)
    mock_client.send_message.assert_called_once_with(
        {"type": "join_lobby", "game_id": 444444, "username": "test_client"}
    )


# =============================================================================
# Test: observe_lobby sends the correct message.
# =============================================================================
def test_observe_lobby(mock_client):
    mock_client.send_message = Mock()
    mock_client.username = "observer"
    mock_client.observe_lobby(555555)
    mock_client.send_message.assert_called_once_with(
        {"type": "observe_lobby", "game_id": 555555, "username": "observer"}
    )


# =============================================================================
# Test: finalize_lobby sends correct message when game_state is None.
# =============================================================================
def test_finalize_lobby_no_game_state(mock_client):
    mock_client.send_message = Mock()
    mock_client.game_state = None
    mock_client.finalize_lobby()
    mock_client.send_message.assert_called_once()
    msg = mock_client.send_message.call_args[0][0]
    assert msg["type"] == "finalize_lobby"
    assert msg["game_id"] == mock_client.game_id
    assert "settings" in msg


# =============================================================================
# Test: join_game sends the correct message.
# =============================================================================
def test_join_game(mock_client):
    mock_client.send_message = Mock()
    mock_client.join_game(666666)
    mock_client.send_message.assert_called_once_with(
        {"type": "join_game", "game_id": 666666}
    )


# =============================================================================
# Test: update_local_game_state updates game_state.
# =============================================================================
def test_update_local_game_state(mock_client, monkeypatch):
    from hanabi.utils import lib

    monkeypatch.setattr(lib, "dict_to_game", lambda d: d)
    new_state = {"log_message": "updated state"}
    mock_client.update_local_game_state(new_state)
    assert mock_client.game_state == new_state


# =============================================================================
# Test: update_game_state sends the correct message.
# =============================================================================
def test_update_game_state(mock_client, monkeypatch):
    mock_client.send_message = Mock()
    mock_client.game_id = 777777
    mock_client.game_state = {"state": "update"}
    from hanabi.utils import lib

    monkeypatch.setattr(lib, "class_to_dict", lambda obj: obj)
    mock_client.update_game_state()
    mock_client.send_message.assert_called_once()
    msg = mock_client.send_message.call_args[0][0]
    assert msg["type"] == "game_state_update"
    assert msg["game_id"] == 777777
    assert msg["game_state"] == {"state": "update"}


# =============================================================================
# Test: play_card sends the correct message.
# =============================================================================
def test_play_card(mock_client):
    mock_client.send_message = Mock()
    mock_client.game_id = 888888
    mock_client.play_card(2)
    mock_client.send_message.assert_called_once_with(
        {"type": "play_card", "game_id": 888888, "card_index": 2}
    )


# =============================================================================
# Test: discard_card sends the correct message.
# =============================================================================
def test_discard_card(mock_client):
    mock_client.send_message = Mock()
    mock_client.game_id = 999999
    mock_client.discard_card(1)
    mock_client.send_message.assert_called_once_with(
        {"type": "discard_card", "game_id": 999999, "card_index": 1}
    )


# =============================================================================
# Test: give_hint sends the correct message.
# =============================================================================
def test_give_hint(mock_client):
    mock_client.send_message = Mock()
    mock_client.game_id = 101010
    mock_client.give_hint("target_player", "color", "red")
    mock_client.send_message.assert_called_once_with(
        {
            "type": "give_hint",
            "game_id": 101010,
            "target_player": "target_player",
            "hint_type": "color",
            "hint_value": "red",
        }
    )


# =============================================================================
# Test: render_gui creates and runs the GUI.
# =============================================================================
@patch("hanabi.gui.gui_launcher.GUI")
def test_render_gui(mock_gui_class, mock_client):
    mock_gui_instance = Mock()
    mock_gui_instance.current_screen = ""
    mock_gui_class.return_value = mock_gui_instance
    mock_client.render_gui()
    mock_gui_instance.run.assert_called_once()
