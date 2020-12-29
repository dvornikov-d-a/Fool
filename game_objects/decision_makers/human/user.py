import asyncio

import config as c
from events_handler import EventsHandler

from game_objects.decision_makers.player import Player
from game_objects.button import Button


class User(Player, EventsHandler):
    def __init__(self, hand, table, is_offensive):
        Player.__init__(self, hand, table, is_offensive)
        EventsHandler.__init__(self, active=False)
        self.show_hand()

        self._self_info = None
        self._opponent_info = None
        self._opponent_cards_count = 0
        self._available_decisions = []

        def on_finish_turn_button_clicked(self):
            self._finish_turn_button_clicked = True

        self._finish_turn_button_clicked = False
        if self.at_bottom:
            finish_button_y = self._hand.top - c.main_menu_button_h
        else:
            finish_button_y = self._hand.bottom
        self.finish_turn_button = Button(self._hand.left, finish_button_y, c.main_menu_button_w, c.main_menu_button_h,
                                         'Завершить ход', lambda button: on_finish_turn_button_clicked(self), padding=5,
                                         active=False)

    def react(self, self_info, opponent_info, opponent_cards_count, available_decisions):
        if not self.active:
            self._self_info = self_info
            self._opponent_info = opponent_info
            self._opponent_cards_count = opponent_cards_count
            self._available_decisions = available_decisions
            self._hand.enable_cards_only_in(available_decisions)
            self.enable()
        if self.is_offensive:
            if not any(self_info):
                self.finish_turn_button.disable()
            else:
                self.finish_turn_button.enable()
        else:
            if not any(opponent_info):
                self.finish_turn_button.disable()
            else:
                self.finish_turn_button.enable()

    def _react(self):
        if self._hand.table_card is not None:
            # Пользователь принял решение положить карту на стол
            self.disable()
            table_card = self._hand.get_table_card()
            self._table.put_card(table_card, self.at_bottom)
        elif self._finish_turn_button_clicked:
            self._finish_turn_button_clicked = False
            # Пользователь принял решение завершить ход
            self.disable()
            if self._is_offensive:
                # Пользователь -- нападающий
                if len(self._self_info) == len(self._opponent_info):
                    # Противник успешно отбился
                    self._table.beat_cards()
                else:
                    # Такая ситуция невозможна (см. Player.listen)
                    pass
            else:
                # Пользователь -- отбивающийся
                if len(self._self_info) < len(self._opponent_info):
                    # Есть неотбитые карты
                    # Пользователь принял решение взять карты
                    self._take_all_cards()

    def _wait(self):
        self._hand.disable_cards()

    def _handle_mouse_button_up(self, button, pos):
        self._react()

    def enable(self):
        EventsHandler.enable(self)
        self.finish_turn_button.enable()

    def disable(self):
        EventsHandler.disable(self)
        self.finish_turn_button.disable()

    def fill_hand(self, new_cards):
        Player.fill_hand(self, new_cards)
        self.show_hand()
