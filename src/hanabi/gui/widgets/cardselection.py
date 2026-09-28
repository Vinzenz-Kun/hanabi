class CardSelection:
    """Selected Card storage"""

    def __init__(self) -> None:
        """
        Initializes a CardSelection object.

        :return: None
        """
        self.player = None
        self.index = None

    def set_selection(self, player: str, index: int) -> None:
        """
        Sets the selected card based on the provided player and index.

        :param player: The name of the player who owns the card.
        :param index: The index of the card in the player's hand.
        :return: None
        """
        self.player = player
        self.index = index

    def clear_selection(self) -> None:
        """
        Clears the selected card.

        :return: None
        """
        self.player = None
        self.index = None

    @property
    def is_selected(self) -> bool:
        """
        Property to check if a card is currently selected.

        :return: True if a card is selected, False otherwise.
        """
        return self.player is not None
