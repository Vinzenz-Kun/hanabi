import json
import os
import sys
import pygame
from hanabi.core.game import Game  # Import the Game class used for state management
from hanabi.utils.lib import class_to_dict
from hanabi.utils.lib import (
    dict_to_game,
)  # Ensure these conversion methods are correctly implemented in lib


def _save_dir() -> str:
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, "saved_games")


class GameStateManager:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    SAVE_DIR = _save_dir()

    @staticmethod
    def ensure_save_directory() -> None:
        """
        Ensures the directory for saving game states exists.

        :return: None
        """
        if not os.path.exists(GameStateManager.SAVE_DIR):
            os.makedirs(GameStateManager.SAVE_DIR)

    @staticmethod
    def get_saved_games() -> list:
        """
        Returns a list of all saved game files.

        :return: List of filenames of saved games.
        """
        GameStateManager.ensure_save_directory()
        return [f for f in os.listdir(GameStateManager.SAVE_DIR) if f.endswith(".json")]

    @staticmethod
    def get_players(filename: str) -> list:
        """
        Retrieves a list of player names from a saved game file.

        :param filename: The filename of the saved game from which to retrieve player names.
        :return: A list of player names.
        """

        game = GameStateManager.load_game_state(filename)

        return game["player_names"]

    @staticmethod
    def save_game_state(game: Game, filename: str) -> None:
        """
        Saves the current game state to a JSON file.

        :param game: The Game object containing the current state.
        :param filename: The name of the file to save the state to.
        :return: None
        """
        GameStateManager.ensure_save_directory()
        filepath = os.path.join(GameStateManager.SAVE_DIR, filename)

        game_state = class_to_dict(game)  # Convert the Game object to a dictionary
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(game_state, file, ensure_ascii=False, indent=4)

    @staticmethod
    def load_game_state(filename: str) -> Game:
        """
        Loads a saved game state from a JSON file.

        :param filename: The name of the file to load the state from.
        :return: A Game object initialized with the loaded state.
        """
        filepath = os.path.join(GameStateManager.SAVE_DIR, filename)

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"The file {filepath} was not found.")

        with open(filepath, "r", encoding="utf-8") as file:
            game_state = json.load(file)

        return game_state

    @staticmethod
    def can_load_game() -> bool:
        """
        Checks if any saved games are available for loading.

        :return: True if at least one saved game exists, otherwise False.
        """
        return bool(GameStateManager.get_saved_games())
