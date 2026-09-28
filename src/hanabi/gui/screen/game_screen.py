import pygame
from hanabi.gui.widgets.cardselection import CardSelection
from hanabi.gui.widgets.colors import Colors as colors
from hanabi.gui.widgets.cardselection import CardSelection
from hanabi.gui.widgets.game_data_access import GameDataAccess
from hanabi.gui.widgets.timer import Timer
from hanabi.utils.state_manager import GameStateManager


class GameScreen:
    chatmessages = []

    def __init__(self, gui) -> None:
        """
        Initializes the GameScreen class with default settings and links it to the client.

        :param gui: The parent GUI instance.
        :type gui: hanabi.gui.gui_launcher.GUI
        :return: None
        """

        self.gui = gui
        self.client = gui.client
        self.data_service = GameDataAccess(self.client)
        self.font = self.gui.font
        self.colors = {
            "black": colors.black,
            "white": colors.white,
            "blue": colors.blue,
            "green": colors.green,
            "gray": colors.gray,
            "red": colors.red,
            "colorful": colors.colorful,
        }
        self.create_ui_elements()
        self.selected_card = CardSelection()
        # self.chatmessages = []  # Store log messages
        self.log_scroll_offset = 0  # Scroll offset for the log

        self.timer = Timer()

        self.timer.timer_active = self.gui.client.lobby_settings.get("timer_active")
        self.timer.time_limit = self.gui.client.lobby_settings.get("timer_seconds")
        self.last_player_index = None
        self.observtarget = None

    def create_ui_elements(self) -> None:
        """
        Creates the UI elements for the game screen, such as the play, discard, and hint buttons,
        as well as the log area at the bottom of the screen.

        :return: None
        """
        self.play_button = pygame.Rect(400, 200, 120, 40)
        self.discard_button = pygame.Rect(400, 260, 120, 40)
        self.log_area = pygame.Rect(
            20, self.gui.window_height - 130, self.gui.window_width - 40, 110
        )
        self.watch_all_button = pygame.Rect(400, 150, 120, 40)
        self.exit_button = pygame.Rect(600, 460, 160, 40)
        self.language_button = pygame.Rect(self.gui.window_width - 200, 20, 180, 40)

    def render(self) -> None:
        """
        Renders the complete game screen with all essential game elements.

        :return: None
        """
        # Clear screen and set caption
        pygame.display.set_caption(self.gui.language_config.get_translation("game"))
        self.gui.window.fill(self.colors["black"])

        # Draw game components
        self.draw_tokens()
        self.draw_discard_pile()
        self.draw_played_piles()
        self.draw_player_hands()
        self.draw_current_turn()
        if not self.observing:
            self.draw_action_buttons()
        self.draw_endgame_conditions()
        self.draw_log_block()
        if self.observing:
            self.draw_watch_all_button()

        pygame.draw.rect(self.gui.window, (200, 200, 200), self.language_button)
        language_text = self.font.render(
            self.gui.language_config.get_translation("Change Language"), True, (0, 0, 0)
        )
        self.gui.window.blit(language_text, (self.gui.window_width - 190, 30))

    def draw_tokens(self) -> None:
        """
        Draws the hint and storm tokens on the game screen.

        :return: None
        """
        hint_tokens = self.client.game_state.hint_token
        storm_tokens = self.client.game_state.storm_token
        remaining_deck_cards = len(self.client.game_state.deck)

        hint_text = self.font.render(
            f"{self.gui.language_config.get_translation('hints')}: {hint_tokens}",
            True,
            self.colors["white"],
        )
        storm_text = self.font.render(
            f"{self.gui.language_config.get_translation('storm_tokens')}: {storm_tokens}",
            True,
            self.colors["white"],
        )
        deck_text = self.font.render(
            f"{self.gui.language_config.get_translation('remaining_cards')}: {remaining_deck_cards}",
            True,
            self.colors["white"],
        )
        self.gui.window.blit(hint_text, (20, 20))
        self.gui.window.blit(storm_text, (200, 20))
        self.gui.window.blit(deck_text, (380, 20))

    def draw_discard_pile(self) -> None:
        """
        Draws the discard pile.

        :return: None
        """
        discard_pile = self.client.game_state.discard_pile
        for i, card in enumerate(discard_pile):
            card_rect = pygame.Rect(20 + (i % 16) * 25, 80 + (i // 16) * 25, 20, 20)
            if isinstance(card, dict):
                card_color = card["color"]
                card_valuuue = str(card["value"])
            else:
                card_color = card.color
                card_valuuue = str(card.value)
            if card_color == "colorful":
                card_color = self.colors["colorful"]
            pygame.draw.rect(self.gui.window, card_color, card_rect)
            card_value = self.font.render(card_valuuue, True, self.colors["black"])
            self.gui.window.blit(card_value, (card_rect.x, card_rect.y))
        discard_text = self.font.render(
            self.gui.language_config.get_translation("discard_pile")
            + f" {len(discard_pile)} "
            + self.gui.language_config.get_translation("cards"),
            True,
            self.colors["white"],
        )
        self.gui.window.blit(discard_text, (20, 50))

    def draw_played_piles(self) -> None:
        """
        Draws the played fireworks piles.

        :return: None
        """
        played_piles = self.client.game_state.fireworks
        self.gui.window.blit(
            self.font.render(
                self.gui.language_config.get_translation("fireworks"),
                True,
                self.colors["white"],
            ),
            (20, 220),
        )
        for i, (color, pile) in enumerate(played_piles.items()):
            card_rect = pygame.Rect(20 + i * 40, 250, 30, 30)
            card_color = color
            if card_color == "colorful":
                card_color = self.colors["colorful"]
            pygame.draw.rect(self.gui.window, card_color, card_rect)
            card_value = self.font.render(str(pile), True, self.colors["black"])
            self.gui.window.blit(card_value, (card_rect.x + 5, card_rect.y + 5))

    def draw_player_hands(self) -> None:
        """
        Displays all players' hands.

        :return: None
        """
        y_offset = 300
        # for player in enumerate(self.client.game_state["players"]):
        for player in self.client.game_state.players:
            if (
                player.name == self.client.username
            ):  # player is a dictionary, like game_state, because it is converted by the method in lib
                hand_text = self.font.render(
                    f"{player.name} {self.gui.language_config.get_translation('your_cards')}",
                    True,
                    self.colors["green"],
                )
            else:
                hand_text = self.font.render(
                    f"{player.name}'s {self.gui.language_config.get_translation('cards')}",
                    True,
                    self.colors["white"],
                )

            self.gui.window.blit(hand_text, (20, y_offset))
            for j, card in enumerate(player.hand):
                if (
                    player.name == self.client.username
                    or player.name == self.observtarget
                ) and card.color_hint == False:
                    card_color = self.colors["gray"]
                else:
                    if card.color == "colorful":
                        card_color = self.colors["colorful"]
                    else:
                        card_color = card.color
                card_rect = pygame.Rect(150 + j * 40, y_offset, 30, 50)
                if (
                    player.name == self.client.username
                    or player.name == self.observtarget
                ) and card.value_hint == False:
                    pygame.draw.rect(
                        self.gui.window, card_color, card_rect
                    )  # Hidden hand
                else:
                    pygame.draw.rect(self.gui.window, card_color, card_rect)
                    card_value = self.font.render(
                        str(card.value), True, self.colors["black"]
                    )
                    self.gui.window.blit(
                        card_value, (card_rect.x + 15, card_rect.y + 30)
                    )

            if self.observing:
                watch_button = pygame.Rect(20, y_offset + 30, 80, 30)
                pygame.draw.rect(self.gui.window, (0, 255, 0), watch_button)
                watch_text = self.font.render(
                    self.gui.language_config.get_translation("observe"), True, (0, 0, 0)
                )
                self.gui.window.blit(watch_text, (155, y_offset + 5))
                player.watch_button = watch_button
            y_offset += 60

    def draw_current_turn(self) -> None:
        """
        Highlights and displays the current player's turn on the game screen.

        :return: None
        """
        current_player = None
        for player in self.client.game_state.players:
            if player.number == self.client.game_state.current_player_index:
                current_player = player
                break

        current_index = self.client.game_state.current_player_index
        if self.timer.timer_active:
            if current_index != self.last_player_index:
                self.timer.start()
                self.last_player_index = current_index

            if self.timer.is_active:
                self.timer.draw(self.gui.window, self.gui.window_width - 250, 50)

                if self.timer.time_over():
                    self.handle_timer_expiration()

        if self.client.username == current_player.name:
            turn_text = self.font.render(
                f"{self.gui.language_config.get_translation('your_turn')}",
                True,
                self.colors["green"],
            )
        else:
            turn_text = self.font.render(
                f"{self.gui.language_config.get_translation('waiting_for')} {current_player.name}...",
                True,
                self.colors["red"],
            )
        self.gui.window.blit(turn_text, (20, self.gui.window_height - 200))

    def handle_timer_expiration(self) -> None:
        """
        Handle what happens when the timer expires.
        Automatically move to the next turn.

        :return: None
        """
        try:
            current_player = None
            for player in self.client.game_state.players:
                if player.number == self.client.game_state.current_player_index:
                    current_player = player
                    break

            if self.client.username == current_player.name:
                self.gui.add_log_message(
                    [
                        "timer_expired_message_1",
                        f"{current_player.name}",
                        "timer_expired_message_2",
                        "",
                    ]
                )

                self.client.game_state.storm_token -= 1
                self.client.game_state.valid_round = True

                self.finish_turn()

                self.timer.restart()
        except Exception as e:
            self.gui.handle_error(str(e))

    def draw_action_buttons(self) -> None:
        """
        Displays the Play Card, Hint and Discard Card buttons.

        :return: None
        """
        self.play_button = pygame.Rect(400, 200, 140, 40)
        pygame.draw.rect(self.gui.window, self.colors["blue"], self.play_button)
        play_button_text = self.font.render(
            self.gui.language_config.get_translation("play_card"),
            True,
            self.colors["white"],
        )
        self.gui.window.blit(play_button_text, (self.play_button))
        self.discard_button = pygame.Rect(600, 200, 140, 40)
        pygame.draw.rect(self.gui.window, self.colors["blue"], self.discard_button)
        discard_button_text = self.font.render(
            self.gui.language_config.get_translation("discard_card"),
            True,
            self.colors["white"],
        )
        self.gui.window.blit(discard_button_text, (self.discard_button))

        # Hint choices
        self.hint_color_button = pygame.Rect(400, 300, 140, 40)
        pygame.draw.rect(self.gui.window, self.colors["blue"], self.hint_color_button)
        color_button_text = self.font.render(
            self.gui.language_config.get_translation("Color Hint"),
            True,
            self.colors["white"],
        )
        self.gui.window.blit(color_button_text, self.hint_color_button)
        self.hint_number_button = pygame.Rect(600, 300, 140, 40)
        pygame.draw.rect(self.gui.window, self.colors["blue"], self.hint_number_button)
        number_button_text = self.font.render(
            self.gui.language_config.get_translation("Number Hint"),
            True,
            self.colors["white"],
        )
        self.gui.window.blit(number_button_text, self.hint_number_button)

        pygame.draw.rect(self.gui.window, self.colors["red"], self.exit_button)
        exit_button_text = self.font.render(
            self.gui.language_config.get_translation("exit"), True, self.colors["white"]
        )
        self.gui.window.blit(
            exit_button_text, (self.exit_button.x + 10, self.exit_button.y + 10)
        )

    def draw_watch_all_button(self) -> None:
        """
        Draws the 'Watch All' button on the game screen.

        The button is displayed as a red rectangle with the text 'Watch All'
        in white. It allows the player to observe all players' hands.

        :return: None
        """
        pygame.draw.rect(self.gui.window, (255, 0, 0), self.watch_all_button)
        watch_all_text = self.font.render(
            self.gui.language_config.get_translation("watch_all"), True, (255, 255, 255)
        )
        self.gui.window.blit(watch_all_text, (405, 155))

    def draw_endgame_conditions(self) -> None:
        """
        Checks and displays endgame conditions.
        If the game is over, the method sends a 'game_ended' message to the server, clears the chat log, sets the result data on the 'result' screen, and transitions to the 'result' screen.

        :return: None
        """
        game_over_data = self.client.game_state.check_game_over()
        overcheck = self.client.game_state.game_over

        if overcheck == True:
            self.client.send_message({"type": "game_ended", **game_over_data})
            GameScreen.chatmessages.clear()
            self.gui.screens["result"].set_result_data(game_over_data)
            self.gui.current_screen = "result"
            # self.logger.info("Transitioning to result screen.")

    def draw_log_block(self) -> None:
        """
        Draws the log block in the bottom left corner of the window.

        The log block displays the last 5 messages in the chat log. If there are more than 5 messages, a scrollbar is displayed on the right side of the log area, allowing the user to scroll up and down through the log.

        :return: None
        """
        log_area_rect = pygame.Rect(
            20, self.gui.window_height - 130, self.gui.window_width - 40, 110
        )
        pygame.draw.rect(self.gui.window, self.colors["gray"], log_area_rect)

        # Draw scrollbar if messages exceed visible area
        max_visible_messages = 5
        if len(self.chatmessages) > max_visible_messages:
            scrollbar_height = log_area_rect.height * (
                max_visible_messages / len(self.chatmessages)
            )
            scrollbar_y = (
                log_area_rect.y
                + (self.log_scroll_offset / len(self.chatmessages))
                * log_area_rect.height
            )
            pygame.draw.rect(
                self.gui.window,
                self.colors["black"],
                (log_area_rect.right - 15, scrollbar_y, 10, scrollbar_height),
            )

        # Render and display visible messages
        translated_message = []
        for chat in self.chatmessages:
            while len(chat) < 4:
                chat.append("")
            translated_message.append(
                self.gui.language_config.get_translation(chat[0])
                + chat[1]
                + self.gui.language_config.get_translation(chat[2])
                + chat[3]
            )

        visible_messages = translated_message[
            -max_visible_messages
            - self.log_scroll_offset : len(self.chatmessages)
            - self.log_scroll_offset
        ]
        for i, msg in enumerate(visible_messages):
            text_surface = self.font.render(msg, True, self.colors["blue"])
            self.gui.window.blit(
                text_surface, (log_area_rect.x + 10, log_area_rect.y + 10 + i * 20)
            )

    def add_log_message(chat: list[str]) -> None:
        """
        Adds a new log message to the game's log block.

        :param chat: A list of strings, with the first string being the player name,
            the second string being the action, the third string being the card played,
            and the fourth string being the message.
        """

        GameScreen.chatmessages.append(chat)
        if len(GameScreen.chatmessages) > 100:  # Limit log history
            GameScreen.chatmessages.pop(0)

    def handle_input(self, events: list[pygame.event.Event]) -> None:
        """
        Handles user interactions on the game screen.

        :param events: A list of pygame events to handle
        :return: None
        """
        try:
            for event in events:
                self.gui.handle_generic_input(event)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    if self.language_button.collidepoint(mouse_pos):
                        self.gui.toggle_language()

                    if not self.observing and self.exit_button.collidepoint(mouse_pos):
                        self.client.handle_disconnect()
                        self.gui.current_screen = "server_connect"

                        # Scroll log messages
                    if event.button == 4:  # Scroll up
                        self.log_scroll_offset = max(0, self.log_scroll_offset - 1)
                    elif event.button == 5:  # Scroll down
                        self.log_scroll_offset = min(
                            len(self.chatmessages) - 5, self.log_scroll_offset + 1
                        )

                    # Handle Play Card button click
                    if not self.observing:
                        if self.play_button.collidepoint(mouse_pos):
                            self.play_selected_card()

                        # Handle Discard Card button click
                        elif self.discard_button.collidepoint(mouse_pos):
                            self.discard_selected_card()

                        # Handle Give Hint
                        if self.hint_color_button.collidepoint(mouse_pos):
                            self.hint_action_choice = 2
                            self.give_hint_to_player()
                        elif self.hint_number_button.collidepoint(mouse_pos):
                            self.hint_action_choice = 3
                            self.give_hint_to_player()

                        self.handle_card_selection(mouse_pos)

                    if self.observing:
                        if self.watch_all_button.collidepoint(mouse_pos):
                            self.observtarget = None

                        for player in self.client.game_state.players:
                            if hasattr(
                                player, "watch_button"
                            ) and player.watch_button.collidepoint(mouse_pos):
                                self.observtarget = player.name

                if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    # save game by pressing s
                    if self.client.game_state:
                        filename = f"save_{self.client.game_id}.json"
                        GameStateManager.save_game_state(
                            self.client.game_state, filename
                        )
                        self.gui.show_popup(
                            f"{self.gui.language_config.get_translation('saved_game')} {filename}"
                        )
                        self.client.logger.info(f"Game state saved to {filename}")

        except Exception as e:
            self.gui.current_screen = "server_connect"
            self.client.handle_disconnect()

    def handle_card_selection(self, mouse_pos: tuple[int, int]):
        """
        Handles mouse clicks on the game screen to select a card from the hand
        to play or discard.

        :param mouse_pos: The position of the mouse click
        :return: None
        """
        self.selected_card.clear_selection()
        # Handle clicking on hand cards to select a card
        y_offset = 300  # Needs to be same position as in draw_player_hands
        for player_index, player in enumerate(self.client.game_state.players):
            current_y = y_offset + (player_index * 60)
            for i, card in enumerate(player.hand):
                card_rect = pygame.Rect(150 + i * 40, current_y, 30, 50)
                if card_rect.collidepoint(mouse_pos):
                    self.selected_card.set_selection(player.name, i)

    def play_selected_card(self) -> None:
        """
        Plays the selected card with validation and updates the game state.

        :return: None
        """
        try:
            if not self.selected_card.is_selected:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("No card selected")
                )
                return

            current_player_name = self.data_service.get_current_player_name()

            if current_player_name != self.client.username:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("Not your turn")
                )
                return

            if self.selected_card.player != self.client.username:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("Not your card")
                )
                return

            self.client.game_state.play_card(
                self.data_service.get_current_player(), self.selected_card.index
            )
            if self.client.game_state.valid_round:
                # self.chatmessages.append(f"Player {current_player_name} played card {self.selected_card} {self.selected_card.index}")
                self.finish_turn()

            self.selected_card.clear_selection()
        except Exception as e:
            self.gui.handle_error(str(e))

    def discard_selected_card(self) -> None:
        """
        Discards the selected card, restores a hint token, and updates the game state.

        :return: None
        """
        try:
            if not self.selected_card.is_selected:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("No card selected")
                )
                return

            current_player_name = self.data_service.get_current_player_name()

            if current_player_name != self.client.username:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("Not your turn")
                )
                return

            if self.selected_card.player != self.client.username:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("Not your card")
                )
                return

            try:
                self.client.game_state.discard(
                    self.data_service.get_current_player(), self.selected_card.index
                )
            except ValueError:
                self.gui.show_popup(
                    self.gui.language_config.get_translation(
                        "Cannot discard. Maximum number of hints reached"
                    )
                )
                return

            if self.client.game_state.valid_round:
                self.finish_turn()
            else:
                return

            self.selected_card.clear_selection()

        except Exception as e:
            self.gui.handle_error(str(e))

    def finish_turn(self) -> None:
        """
        Finishes the current player's turn.

        Checks if the game is over and ends the game if it is. Otherwise, it increments the current player index and moves on to the next player's turn.

        :return: None
        """
        if self.client.game_state.valid_round:
            self.client.game_state.finish_turn()
            game_over = self.client.game_state.check_game_over()
            self.gui.client.logger.info(game_over)
            if not game_over == {"game_over": False}:
                self.client.send_message(game_over)
            self.client.update_game_state()
        else:
            return

    def highlight_hint_cards(self, player, hint_type: str, hint_value: str):
        """
        Visually highlights cards that match the given hint.

        :param player: The player to check
        :type player: Player
        :param hint_type: The type of hint to check (color or value)
        :param hint_value: The value of the hint (e.g. 'Red' or '2')
        :return: None
        """
        for i, card in enumerate(player.name):
            if getattr(card, hint_type) == hint_value:
                card_rect = pygame.Rect(150 + i * 60, 300, 50, 80)
                pygame.draw.rect(self.window, self.colors["yellow"], card_rect, 5)
                pygame.display.update()

    def check_fireworks_completion(self) -> bool:
        """
        Checks if all fireworks piles are completed.

        :return: True if all fireworks piles are completed, False otherwise
        """
        if self.game_state.game_over:
            return True
        return False

    def give_hint_to_player(self) -> None:
        """
        Allows the player to give hints to other players interactively.

        :return: None
        """
        try:
            if not self.selected_card.is_selected:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("No card selected")
                )
                return

            current_player_name = self.data_service.get_current_player_name()

            if current_player_name != self.client.username:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("Not your turn")
                )
                return

            if self.selected_card.player == self.client.username:
                self.gui.show_popup(
                    self.gui.language_config.get_translation("Can't hint yourself")
                )
                return

            if self.hint_action_choice == 2:
                hint_type = "color"
            elif self.hint_action_choice == 3:
                hint_type = "value"

            self.selected_card.index

            to_player = self.data_service.get_player(self.selected_card.player)

            valid_players = [
                p
                for p in self.client.game_state.players
                if p.name != self.client.username
            ]
            if not valid_players:
                return
            self.client.game_state.give_hint(
                to_player, hint_type, self.selected_card.index
            )
            if self.client.game_state.valid_round:
                self.finish_turn()
            else:
                return

            self.hint_action_choice = 0
            self.selected_card.clear_selection()

        except Exception as e:
            self.gui.handle_error(str(e))

    def reset_game_ui(self) -> None:
        """
        Reset all game-related UI elements to their initial state.

        :return: None
        """
        self.selected_card.clear_selection()
        self.log_messages = []
        self.logger.info("Game UI reset for new session.")
