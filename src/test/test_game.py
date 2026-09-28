import pytest

from hanabi.core.game import Player, Card, Game


# Fixtures for reusable setup
def create_game():
    return Game(
        game_id=1,
        num_players=2,
        player_names=["Alice", "Bob"],
        hint_tokens=8,
        storm_tokens=3,
        color_rush=False,
    )


# Test Player Initialization
def test_player_initialization():
    player = Player("Alice", 1)
    assert player.name == "Alice"
    assert player.number == 1
    assert player.hand == []


# Test Card Initialization
def test_card_initialization():
    card = Card("red", 3, color_hint=True)
    assert card.color == "red"
    assert card.value == 3
    assert card.color_hint is True
    assert card.value_hint is False


# Test Game Initialization
def test_game_initialization():
    game = create_game()
    assert game.num_players == 2
    assert len(game.players) == 2
    assert game.hint_token == 8
    assert game.storm_token == 3
    assert len(game.deck) > 0


# Test Play Card - Successful Play
def test_play_card_success():
    game = create_game()
    player = game.players[0]
    card = Card("red", 1)
    player.hand = [card]
    game.fireworks = {color: 0 for color in ["white", "yellow", "green", "blue", "red"]}

    game.play_card(player, 0)

    assert game.fireworks["red"] == 1
    assert len(player.hand) == 1  # Drew a new card
    assert game.storm_token == 3


# Test Play Card - Failed Play
def test_play_card_fail():
    game = create_game()
    player = game.players[0]
    card = Card("red", 2)
    player.hand = [card]
    game.fireworks = {color: 0 for color in ["white", "yellow", "green", "blue", "red"]}

    game.play_card(player, 0)

    assert game.fireworks["red"] == 0
    assert len(player.hand) == 1  # Drew a new card
    assert game.storm_token == 2  # Lost a storm token
    assert len(game.discard_pile) == 1


# Test Discarding a Card
def test_discard_card():
    game = create_game()
    player = game.players[0]
    card = Card("blue", 3)
    player.hand = [card]
    game.hint_token = 5

    game.discard(player, 0)

    assert len(player.hand) == 1  # Drew a new card
    assert len(game.discard_pile) == 1
    assert game.hint_token == 6


# Test Giving Hint - Color
def test_give_hint_color():
    game = create_game()
    player = game.players[0]
    player.hand = [Card("red", 2), Card("blue", 3)]

    hints = game.give_hint(player, "color", 0)

    assert len(hints) == 1
    assert hints[0][1].color_hint is True
    assert game.hint_token == 7


# Test Giving Hint - Value
def test_give_hint_value():
    game = create_game()
    player = game.players[0]
    player.hand = [Card("red", 2), Card("blue", 2)]

    hints = game.give_hint(player, "value", 0)

    assert len(hints) == 2
    assert hints[0][1].value_hint is True
    assert hints[1][1].value_hint is True
    assert game.hint_token == 7


# Test Game Over Conditions
def test_game_over_victory():
    game = create_game()
    game.fireworks = {color: 5 for color in ["white", "yellow", "green", "blue", "red"]}

    result = game.check_game_over()

    assert game.is_victory is True
    assert game.game_over is True
    assert result["reason"] == "victory"


# Test Score Calculation
def test_calculate_score():
    game = create_game()
    game.fireworks = {"red": 3, "blue": 2, "green": 4, "yellow": 1, "white": 0}

    score = game.calculate_score()

    assert score == 10
