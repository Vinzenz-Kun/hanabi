from dataclasses import dataclass
import random
import hanabi.utils.lib as lib


@dataclass
class Player:
    def __init__(self, name: str, number: int, hand=None) -> None:
        """
        Initializes a player with a given name and number.

        :param name: The name of the player.
        :param number: The number of the player (of order).
        :param hand: The starting hand of the player. If None, the player starts with an empty hand.
        :return: None
        """
        self.name = name  # Initialize via GUI
        self.number = number  # Player number (of order)
        if hand is None:  # List of Card objects
            self.hand = []
        else:
            self.hand = hand


@dataclass
class Card:
    def __init__(
        self, color: str, value: int, color_hint=False, value_hint=False
    ) -> None:
        """
        Initializes a Card object with a given color and value.

        :param color: The color of the card.
        :param value: The value of the card.
        :param color_hint: Whether the color of the card is hinted.
        :param value_hint: Whether the value of the card is hinted.
        :return: None
        """
        self.color = color  # Set in __init__
        self.value = value
        if color_hint:  # Hint flag, set in give_hint
            self.color_hint = True
        else:
            self.color_hint = False

        if value_hint:  # Hint flag, set in give_hint
            self.value_hint = True
        else:
            self.value_hint = False


class Game:
    def __init__(
        self,
        game_id: int,
        num_players: int,
        player_names: list,
        hint_tokens: int,
        storm_tokens: int,
        color_rush: bool,
        resources=None,
    ) -> None:
        """
        Initializes a new game with the given parameters.

        :param game_id: The game ID for this game.
        :param num_players: The number of players in the game.
        :param player_names: The list of player names. If None, the players are named 'Player1', 'Player2', etc.
        :param hint_tokens: The number of hint tokens available at the start of the game.
        :param storm_tokens: The number of storm tokens available at the start of the game.
        :param color_rush: Whether the color rush variant is enabled.
        :param resources: An optional dictionary of resources to use for the game, such as the deck, player hands, fireworks, etc. If None, the game is initialized with a standard deck and player hands.
        :return: None
        """
        colors = ["white", "yellow", "green", "blue", "red"]
        self.color_rush = color_rush
        if self.color_rush:
            colors.append("colorful")
        # Game state initialization
        self.game_ID = game_id
        self.num_players = num_players
        self.player_names = player_names
        self.players = []
        self.deck = []
        self.game_over = False
        self.is_victory = False
        self.fireworks = {}
        self.hint_token = hint_tokens  # Available hints, refreshed at successful play
        self.storm_token = storm_tokens  # Available "lives" until knockout
        self.discard_pile = []
        self.log_message = []

        self.final_round_counter = 99999

        self.count_discard_pile = 0
        self.score = 0

        # Initial game setup
        if resources is None:
            self.deck = [
                Card(color, value)
                for color in colors
                for value in [1, 1, 1, 2, 2, 3, 3, 4, 4, 5]
            ]
            # Game resources
            self.fireworks = {
                color: 0 for color in colors
            }  # Empty card stacks at start
            self.discard_pile = []
            self.count_draw_pile = len(self.deck)
            self.max_hint_tokens = hint_tokens

            random.shuffle(self.deck)  # Shuffle the deck defined above
            if player_names is None:
                self.players = [
                    Player(f"Player{i+1}", i + 1) for i in range(num_players)
                ]
            else:
                i = 0
                for player in player_names:
                    self.players.append(Player(player, i))
                    i += 1
            self.current_player_index = 0
            # Add cards to player hands
            hand_size = 5 if len(self.players) <= 3 else 4
            for player in self.players:
                for i in range(hand_size):
                    player.hand.append(self.deck.pop())

        # Transmitted game state
        else:
            self.deck = resources["deck"]
            self.players = resources["players"]
            self.game_over = resources["game_over"]
            self.is_victory = resources["is_victory"]
            self.fireworks = resources["fireworks"]
            self.hint_token = resources["hint_token"]
            self.storm_token = resources["storm_token"]
            self.discard_pile = resources["discard_pile"]
            self.count_discard_pile = resources["count_discard_pile"]
            self.count_draw_pile = resources["count_draw_pile"]
            self.score = resources["score"]
            self.current_player_index = resources["current_player_index"]
            self.final_round_counter = resources["final_round_counter"]
            self.max_hint_tokens = resources["max_hint_tokens"]

    def play_card(self, player: Player, card_index: int) -> None:
        """
        Plays a card from the player's hand.

        :param player: The player whose card we are playing
        :param card_index: The index of the card in the player's hand to play
        :return: None
        """
        card = player.hand.pop(card_index)

        if self.fireworks[card.color] + 1 == card.value:
            self.fireworks[card.color] += 1
            self.log_message = [
                "good play",
                f":  {player.name}  ",
                f"{card.color}",
                f"{card.value}",
            ]

            if card.value == 5 and self.hint_token < 8:
                self.hint_token += 1

        else:
            self.log_message = [
                "bad play",
                f":  {player.name}  ",
                f"{card.color}",
                f"{card.value}",
            ]
            self.storm_token -= 1
            self.discard_pile.append(card)

            if self.storm_token == 0:
                self.game_over = True

        if self.deck:
            player.hand.append(self.deck.pop())
            if (
                not self.deck and self.final_round_counter >= 999
            ):  # Just drew the last card, start last turns
                self.final_round_counter = len(self.players)
                self.log_message.append("final round")
            elif not self.deck:
                if self.final_round_counter >= -999:
                    self.final_round_counter -= 1
        self.valid_round = 1

    def discard(self, player: Player, card_index: int) -> list:
        """
        Discards a card from the player's hand, restores a hint token, and updates the game state.

        :param player: The player whose card is being discarded
        :param card_index: The index of the card in the player's hand to discard
        :return: An empty list if the maximum number of hint tokens is reached
        """
        if self.hint_token < self.max_hint_tokens:
            card = player.hand.pop(card_index)
            self.discard_pile.append(card)

            self.log_message = [
                "discarded",
                f":  {player.name}  ",
                f"{card.color}",
                f"{card.value}",
            ]
            self.hint_token += 1

            if self.deck:
                player.hand.append(self.deck.pop())
                if (
                    not self.deck and self.final_round_counter >= 999
                ):  # Just drew the last card, start last turns
                    self.final_round_counter = len(self.players)
                    self.log_message.append("final round")
                elif not self.deck:
                    if self.final_round_counter >= -999:
                        self.final_round_counter -= 1
            self.valid_round = 1
        elif self.hint_token == self.max_hint_tokens:
            self.valid_round = 0
            raise ValueError("Cannot discard. Maximum hint tokens reached.")

    def give_hint(self, to_player: Player, hint_type: str, card_index: int) -> list:
        """
        Gives a hint to another player.

        :param to_player: The player receiving the hint
        :param hint_type: The type of hint to give (color or value)
        :param hint_value: The value of the hint (e.g. 'Red' or '2')
        :return: A list of tuples containing the index of the cards in the player's hand that match the hint
        """
        if self.hint_token > 0:
            self.hint_token -= 1
            matching_cards = []
            if hint_type == "color":
                hint_value = to_player.hand[card_index].color
                self.log_message = [
                    "hinted",
                    f"  {to_player.name}:  ",
                    f"{hint_value}",
                    "",
                ]
            if hint_type == "value":
                hint_value = to_player.hand[card_index].value
                self.log_message = [
                    "hinted",
                    f"  {to_player.name}:  ",
                    "",
                    f"{hint_value}",
                ]
            for i, card in enumerate(
                to_player.hand
            ):  # create tuples from target player hand
                if hint_type == "color" and (
                    card.color == hint_value or card.color == "colorful"
                ):
                    card.color_hint = True
                    matching_cards.append((i, card))
                if hint_type == "value" and card.value == hint_value:
                    card.value_hint = True
                    matching_cards.append((i, card))

            self.valid_round = 1

            return matching_cards

        else:
            self.valid_round = 0
            return []

    def finish_turn(self) -> None:
        """
        Finishes the current player's turn.

        Checks if the game is over and ends the game if it is. Otherwise, it increments the current player index and moves on to the next player's turn.

        :return: None
        """
        if self.valid_round == 1:

            self.final_round_counter -= 1
            if self.final_round_counter == -1:
                self.game_over = True
                return
            self.check_game_over()
            self.current_player_index = (self.current_player_index + 1) % len(
                self.players
            )

    def check_game_over(self) -> dict:
        """
        Checks if the game is over.

        Returns a dictionary with the game state. If the game is over, the dictionary contains the reason for the game over, the game ID, whether the game was won or lost, and the final score. If the game is not over, the dictionary contains the game state and the message "game_over_continue".

        The game can end in three ways:

        * The deck is empty and all players have played all their cards.
        * The storm tokens are all used up.
        * All the fireworks stacks have been completed (all values are 5).

        :return: A dictionary with the game state.
        """
        if not self.deck:
            if self.final_round_counter == -1:
                self.game_over = True
                return {
                    "type": "game_ended",
                    "reason": "game_over_defeat",
                    "game_id": self.game_ID,
                    "is_victory": False,
                    "final_score": self.calculate_score(),
                    "game_state": lib.class_to_dict(self),
                }

        if self.storm_token == 0:
            self.game_over = True
            return {
                "type": "game_ended",
                "reason": "game_over_defeat",
                "game_id": self.game_ID,
                "is_victory": False,
                "final_score": self.calculate_score(),
                "game_state": lib.class_to_dict(self),
            }

        if all(value == 5 for value in self.fireworks.values()):
            self.is_victory = True
            self.game_over = True
            self.log_message.append("game_over_victory")
            return {
                "type": "game_ended",
                "reason": "victory",
                "game_id": self.game_ID,
                "is_victory": True,
                "final_score": self.calculate_score(),
                "game_state": lib.class_to_dict(self),
            }

        return {"game_over": False}  # Game continues

    def calculate_score(self) -> int:
        """
        Calculates the score of the game.

        If the game is over, this method returns 0. Otherwise, it returns the sum of the values of all the fireworks stacks.

        :return: The score of the game.
        """
        if self.storm_token == 0:
            return 0
        total_score = sum(self.fireworks.values())
        return total_score

    def reset(self) -> None:
        """
        Resets the game state.

        This method is called to reset the game after it has ended. It resets all the game state variables to their initial values.

        :return: None
        """
        self.players = []
        self.current_turn = 0
        self.deck = []
        self.played_piles = {}
        self.hint_tokens = 8
        self.storm_tokens = 3
        self.log_message = []

    # def provide_chat(self):
    #    return self.log_message
