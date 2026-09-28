class GameDataAccess:
    """Retrieve and Store information about the game"""

    from hanabi.core.game import Player

    def __init__(self, client) -> None:
        """
        Initialize the GameDataAccess with the client instance

        :param client: The client instance
        :type client: hanabi.core.client_launcher.Client
        :return: None
        """
        self.client = client

    def get_current_player(self) -> Player:
        """
        Returns the current player object

        :return: The current player object
        """
        for player in self.client.game_state.players:
            if player.number == self.get_current_player_index():
                return player

    def get_current_player_index(self) -> int:
        """
        Returns the current player's number (index)

        :return: The current player's number (index)
        """
        return self.client.game_state.current_player_index

    def get_current_player_name(self) -> str:
        """
        Returns the current player's name

        :return: The current player's name
        """
        for player in self.client.game_state.players:
            if player.number == self.get_current_player_index():
                return player.name

    def get_game_state(self) -> dict:
        """
        Returns the current game state as a dictionary

        :return: The current game state
        """
        return self.client.game_state

    def get_username(self) -> str:
        """
        Returns the username of the current player

        :return: The username of the current player
        """
        return self.client.username

    def get_players(self) -> list:
        """
        Returns a list of Player objects representing all players in the game

        :return: A list of Player objects
        """
        return self.client.game_state.players

    def get_player_hand(self, player_name: str) -> list:
        """
        Retrieves the hand of a specified player.

        :param player_name: The name of the player whose hand is to be retrieved.
        :return: A list representing the player's hand.
        """

        return self.client.game_state.players[player_name].hand

    def get_player(self, player_name: str) -> Player:
        """
        Retrieves a Player object based on the player's name.

        :param player_name: The name of the player to retrieve.
        :return: The Player object corresponding to the specified name, or None if not found.
        """
        for player in self.client.game_state.players:
            if player.name == player_name:
                return player

    def get_card(self, player_name: str, card_index: int) -> Player:
        """
        Retrieves a card from a player's hand based on the player's name and the card's index.

        :param player_name: The name of the player whose card is to be retrieved.
        :param card_index: The index of the card in the player's hand.
        :return: The card at the specified index of the specified player's hand, or None if not found.
        """
        for player in self.client.game_state.players:
            if player.name == player_name:
                return player.hand[card_index]

    def set_current_player_index(self, current_player_index: int) -> None:
        """
        Sets the current player index to the specified value.

        :param current_player_index: The new value for the current player index.
        :return: None
        """
        self.client.game_state.current_player_index = current_player_index
