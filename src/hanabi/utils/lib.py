import logging


def class_to_dict(obj: object) -> dict:
    """
    Recursively converts an object to a dictionary representation.

    :param obj: The object to be converted, which can be an instance of a class,
                a list, or a tuple.
    :return: A dictionary representation of the object if it has a __dict__ attribute,
             a list of dictionaries if the object is a list or tuple, or the object itself
             if it is neither.
    """

    if isinstance(obj, (list, tuple)):
        return [class_to_dict(i) for i in obj]
    elif hasattr(obj, "__dict__"):
        return {key: class_to_dict(value) for key, value in obj.__dict__.items()}
    else:
        return obj


def dict_to_game(game_state: dict):
    """
    Converts a dictionary representation of a game state to a Game object.

    :param game_state: A dictionary representation of a game state.
    :return: A Game object.
    """
    from hanabi.core.game import Card
    from hanabi.core.game import Player
    from hanabi.core.game import Game

    game_id = game_state["game_ID"]
    num_players = game_state["num_players"]
    player_names = game_state["player_names"]
    hint_tokens = game_state["hint_token"]
    storm_tokens = game_state["storm_token"]
    deck = []
    for key in game_state["deck"]:
        deck.append(
            Card(key["color"], key["value"], key["color_hint"], key["value_hint"])
        )
    players = []
    for key in game_state["players"]:
        hand = []
        for card in key["hand"]:
            hand.append(
                Card(
                    card["color"], card["value"], card["color_hint"], card["value_hint"]
                )
            )
        players.append(Player(key["name"], key["number"], hand))
    color_rush = game_state["color_rush"]
    resources = {
        "deck": deck,
        "players": players,
        "game_over": game_state["game_over"],
        "is_victory": game_state["is_victory"],
        "fireworks": game_state["fireworks"],
        "hint_token": game_state["hint_token"],
        "storm_token": game_state["storm_token"],
        "discard_pile": game_state["discard_pile"],
        "count_draw_pile": game_state["count_draw_pile"],
        "count_discard_pile": game_state["count_discard_pile"],
        "score": game_state["score"],
        "current_player_index": game_state["current_player_index"],
        "final_round_counter": game_state["final_round_counter"],
        "max_hint_tokens": game_state["max_hint_tokens"],
    }
    game = Game(
        game_id,
        num_players,
        player_names,
        hint_tokens,
        storm_tokens,
        color_rush,
        resources,
    )
    return game


def setup_logger(name: str, logfile="app.log", level=logging.DEBUG) -> logging.Logger:
    """
    Initializes a logger with the given name and configuration.

    :param name: The name of the logger.
    :param logfile: The name of the log file.
    :param level: The logging level (default is logging.DEBUG).
    :return: The logger object.
    """
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Disables handler duplicates
        logger.setLevel(level)
        handler = logging.FileHandler(logfile, mode="a")
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
    return logger
