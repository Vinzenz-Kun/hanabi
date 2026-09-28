class LanguageConfig:
    def __init__(self) -> None:
        """
        Initialize the language configuration.

        This class stores all the translations for the text that appears in the game GUI.
        The default language is German ('de').

        :return: None
        """

        self.current_language = "de"  # Default to german
        self.translations = {
            "en": {
                "fireworks": "Fireworks",
                "played_cards": "Played Cards",
                "hints": "Hints",
                "storm_tokens": "Storm Tokens",
                "discard_pile": "Discard Pile",
                "your_turn": "Your Turn",
                "waiting_for": "Waiting for",
                "game_over_victory": "Congratulations! You completed all fireworks!",
                "game_over_defeat": "Lost. Try again!",
                "colors": {
                    "red": "Red",
                    "blue": "Blue",
                    "green": "Green",
                    "yellow": "Yellow",
                    "white": "White",
                    "colorful": "Colorful",
                },
                "cards": "Cards",
                "ready": "Ready to start the game!",
                "overcrowded": "Too many players in the lobby...",
                "not_enough": "Not enough players in the lobby...",
                "player": "Player",
                "lobby": "Lobby",
                "game_settings": "Game Settings",
                "join": "Join",
                "new_game": "Create New Game",
                "refresh": "Refresh",
                "game_connect": "Game Connection",
                "open_games": "Open Games",
                "game": "Game",
                "start_game": "Start Game",
                "activate_color_rush": "Activate Color Rush",
                "username": "Username",
                "connection_details": "Connection Details",
                "hanabi_connection": "Hanabi Connection",
                "connect": "Connect",
                "color": "Color",
                "number": "Number",
                "play_card": "Play Card",
                "discard_card": "Discard Card",
                "give_hint": "Give Hint",
                "your_cards": "Your Cards",
                "cards": "Cards",
                "your_turn": "Your Turn!",
                "end": "End",
                "score": "Score",
                "back_to_lobby": "Back to Lobby",
                "oje": "Oje!",
                "weak": "Weak! No applause",
                "ok": "OK! The spectators have seen better",
                "good": "Good! The spectators are amused",
                "great": "Great! The spectators are delighted",
                "legendary": "Legendary! The spectators are in awe",
                "invalid_score": "Invalid score.",
                "good play": "succesfully played by",
                "bad play": "made mistake playing by",
                "discarded": "discarded by",
                "hinted": "hint for",
                "final round": "last round for each player!",
                "red": "Red",
                "blue": "Blue",
                "green": "Green",
                "yellow": "Yellow",
                "white": "White",
                "colorful": "Colorful",
                "observe": "observe",
                "menu_title": "Navigation Menu",
                "server_connect": "Server Connect",
                "game_connect": "Game Connect",
                "lobby": "Lobby",
                "result": "Result",
                "No card selected": "No card selected",
                "Not your turn": "Not your turn",
                "Can't hint yourself": "Can't hint yourself",
                "Not your card": "Not your card",
                "saved_game": "Saved Game",
                "player_mismatch": "Player mismatch",
                "loaded_game": "Loaded Game",
                "activate_timer": "Timer",
                "exit": "Exit Game",
                "exit_menu": "Exit to Menu",
                "invalid_character": "Invalid character. Only letters and numbers are allowed.",
                "Change Language": "Change Language",
                "remaining_cards": "Remaining Cards",
                "Cannot discard. Maximum number of hints reached": "Cannot discard. Maximum number of hints reached",
                "game over": "game over",
                "timer_expired_message_1": "114514",
                "timer_expired_message_2": "1919810",
                "invalid_character_host": "Invalid character. Only letters and numbers are allowed.",
                "invalid_character_port": "Invalid character. Only numbers are allowed.",
                "invalid_port_length": "Invalid port. Please enter a number between 1024 and 65535.",
                "number_hint": "number_hint",
                "color_hint": "color_hint",
                "": "",
            },
            "de": {
                "fireworks": "Feuerwerke",
                "played_cards": "Gespielte Karten",
                "hints": "Hinweise",
                "storm_tokens": "Gewitter-Plättchen",
                "discard_pile": "Ablagestapel",
                "your_turn": "Du bist dran!",
                "waiting_for": "Warten auf",
                "game_over_victory": "Glückwunsch! Ihr habt alle Feuerwerke beendet!",
                "game_over_defeat": "Verloren. Versuche es erneut!",
                "colors": {
                    "red": "Rot",
                    "blue": "Blau",
                    "green": "Grün",
                    "yellow": "Gelb",
                    "white": "Weiß",
                    "colorful": "colorful",
                },
                "cards": "Karten",
                "ready": "Bereit das Spiel zu starten!",
                "overcrowded": "Zu viele Spieler in der Lobby...",
                "not_enough": "Nicht genug Spieler in der Lobby...",
                "player": "Spieler",
                "lobby": "Lobby",
                "game_settings": "Spiel-Einstellungen",
                "join": "Beitreten",
                "new_game": "Neues Spiel erstellen",
                "refresh": "Aktualisieren",
                "game_connect": "Spielverbindung",
                "open_games": "Offene Spiele",
                "game": "Spiel",
                "start_game": "Spiel starten",
                "activate_color_rush": "Farbrausch aktivieren",
                "username": "Benutzername",
                "connection_details": "Verbindungsdetails",
                "hanabi_connection": "Hanabi-Verbindung",
                "connect": "Verbinden",
                "color": "Farbe",
                "number": "Anzahl",
                "play_card": "Karte spielen",
                "discard_card": "Karte ablegen",
                "give_hint": "Hinweis geben",
                "your_cards": "Deine Karten",
                "cards": "Karten",
                "your_turn": "Du bist dran!",
                "end": "Spielende",
                "score": "Punktzahl",
                "back_to_lobby": "Zur Lobby",
                "oje": "Oje! Die Zuschauer buhen.",
                "weak": "Schwach! Kein Applaus.",
                "ok": "OK! Die Zuschauer sind Besseres gewohnt.",
                "good": "Gut! Die Zuschauer sind erfreut.",
                "great": "Sehr gut! Die Zuschauer sind begeistert.",
                "legendary": "Legendär! Die Zuschauer werden diese Show nie vergessen.",
                "invalid_score": "Ungültige Punktzahl.",
                "good play": "Korrekter Zug von",
                "bad play": "Inkorrekter Zug von",
                "discarded": "abwirft von",
                "hinted": "Hinweise für",
                "final round": "Letzter Zug für jeden Spieler!",
                "red": "Rot",
                "blue": "Blau",
                "green": "Grün",
                "yellow": "Gelb",
                "white": "Weiß",
                "colorful": "Bunt",
                "observe": "zuschauen",
                "menu_title": "Navigationsmenü",
                "server_connect": "Serververbindung",
                "game_connect": "Spielverbindung",
                "lobby": "Lobby",
                "result": "Ergebnis",
                "observe": "zuschauen",
                "No card selected": "keine Karte gewählt",
                "Not your turn": "Du bist nicht Dran",
                "Can't hint yourself": "Einr andere hinweisen",
                "Not your card": "Nicht deine Karte",
                "saved_game": "Spielstand gespeichert: ",
                "loaded_game": "Spielstand geladen: ",
                "player_mismatch": "Spieler stimmen nicht überein",
                "activate_timer": "Stoppuhr",
                "exit": "Spiel verlassen",
                "exit_menu": "Zum Menü",
                "invalid_character": "Ungültiges Zeichen. Nur Buchstaben und Zahlen sind erlaubt.",
                "Change Language": "Sprache wechseln",
                "victory": "Gewonnen",
                "remaining_cards": "Verbleibende Karten",
                "Cannot discard. Maximum number of hints reached": "Karte kann nicht abgelegt werden. Maximale Anzahl an Hinweisen erreicht",
                "game over": "Verloren",
                "timer_expired_message_1": "1919810",
                "timer_expired_message_2": "114514",
                "invalid_character_host": "Ungültiges Zeichen. Nur Buchstaben, Zahlen und Punkte sind erlaubt.",
                "invalid_character_port": "Ungültiges Zeichen. Nur Zahlen sind erlaubt.",
                "invalid_port_length": "Die Portnummer muss zwischen 1024 und 65535 liegen.",
                "Color Hint": "Farbhinweis",
                "Number Hint": "Nummerhinweis",
                "": "",
            },
        }

    def set_language(self, language_code: str) -> None:
        """
        Sets the language of the GUI to the given language code.

        :param language_code: The language code to set, e.g. 'en' or 'de'.
        :raises ValueError: If the given language code is not supported. This won't happen in practice.
        :return: None
        """
        if language_code in self.translations:
            self.current_language = language_code
        else:
            raise ValueError(f"Unsupported language: {language_code}")

    def get_translation(self, key: str) -> str:
        """
        Returns the translation of the given key in the current language.

        :param key: The key to translate
        :return: The translated string or the original key if no translation exists
        """
        return self.translations[self.current_language].get(key, key)

    def get_color_translation(self, color: str) -> str:
        """
        Returns the translation of the given color in the current language.

        :param color: The color to translate
        :return: The translated color string or the original color if no translation exists
        """
        return self.translations[self.current_language]["colors"].get(color, color)
