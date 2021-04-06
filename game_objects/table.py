import random
import pygame

import config as c
from game_objects.decision_makers.robot.algo import Algo
from game_objects.deck import Deck
from game_objects.game_object import GameObject
from game_objects.beaten import Beaten
from game_objects.alarm import Alarm


class Table(GameObject):
    def __init__(self, exit_func):
        GameObject.__init__(self,
                            c.hand_offset_x,
                            2 * c.hand_offset_y + c.hand_h,
                            c.hand_w,
                            c.screen_height - 4 * c.hand_offset_y - 2 * c.hand_h)
        self._subscribers = []
        self._beaten = Beaten()
        self._deck = Deck()
        self._trump = random.choice(c.suits)
        bottom_player_pool = []
        top_player_pool = []
        self._players_pools = [bottom_player_pool, top_player_pool]
        self._alarm = Alarm(self.centerx, self.centery - c.font_size // 2)
        self._beat = False
        self._beat_in = 0
        self._exit_func = exit_func

    @property
    def trump(self):
        return self._deck.trump

    @property
    def trump_info(self):
        return self._deck.trump_info

    @property
    def nominals_scores(self):
        return {'6': 6,
                '7': 7,
                '8': 8,
                '9': 9,
                '10': 10,
                'jack': 11,
                'queen': 12,
                'king': 13,
                'ace': 14}

    @property
    def info(self):
        # Формат информации о ситуации на столе:
        # (((suit, nominal), (suit, nominal), (suit, nominal), ...), <-- Нижний игрок
        #  ((suit, nominal), (suit, nominal), (suit, nominal), ...)) <-- Верхний игрок
        return self.bottom_player_info, self.top_player_info

    @property
    def bottom_player_info(self):
        return self._get_player_info(self._players_pools[0])

    @property
    def top_player_info(self):
        return self._get_player_info(self._players_pools[1])

    def opponent_cards_count(self, self_at_bottom):
        for sub in self._subscribers:
            if sub.at_bottom != self_at_bottom:
                return sub.cards_count

    @property
    def _size(self):
        return max(len(self._players_pools[0]), len(self._players_pools[1]))

    # (Интерфейс доступа)
    # Вызывается один раз в начале игры самой же игрой
    def init_game(self, bottom_player, top_player):
        self._subscribers.append(bottom_player)
        self._subscribers.append(top_player)
        self._turn_alarm()
        self._notify(fill_hands=True, what_happened='begin')

    def _settle(self):
        if self._size < 2:
            int_between = 0
        else:
            int_between = min(c.hand_max_int_between_cards,
                              (self.width - 2 * c.hand_offset_x - self._size * c.card_w) // (self._size - 1))
        offset_x = (self.width - 2 * c.hand_offset_x - self._size * c.card_w - int_between * (self._size - 1)) // 2
        for i, card in enumerate(self._players_pools[0]):
            card.move(self.left + c.hand_offset_x + offset_x - card.left + int_between * i + c.card_w * i,
                      self.centery - c.hand_offset_y - card.top)
        for i, card in enumerate(self._players_pools[1]):
            card.move(self.left + c.hand_offset_x + offset_x - card.left + int_between * i + c.card_w * i,
                      self.centery - c.card_h + c.hand_offset_y - card.top)

    def _turn_alarm(self):
        if self._subscribers[0].is_offensive:
            self._alarm.set_text('Ваш ход')
        else:
            self._alarm.set_text('Ход противника')

    def _beaten_alarm(self):
        self._alarm.set_text('Бито')
        self._beat = True
        self._beat_in = c.frame_rate * 2

    @staticmethod
    def _get_player_info(player_pool):
        player_info = []

        for card in player_pool:
            player_info.append(card.info)

        read_only_player_info = tuple(player_info)
        return read_only_player_info

    # (Интерфейс доступа)
    # Положить карту на стол
    def put_card(self, card, at_bottom, opponent_card_index=-1):
        if at_bottom:
            player_pool = self._players_pools[0]
            opponent_pool = self._players_pools[1]
        else:
            player_pool = self._players_pools[1]
            opponent_pool = self._players_pools[0]
        player_pool.append(card)
        # Защита от определённой карты
        if opponent_card_index != -1 and player_pool.index(card) != opponent_card_index:
            player_card_index = player_pool.index(card)
            opponent_card = opponent_pool.pop(opponent_card_index)
            opponent_pool.insert(player_card_index, opponent_card)
        self._settle()
        self._notify(fill_hands=False, what_happened='placed')

    # (Интерфейс доступа)
    # Отдать карты на столе
    def give_all_cards(self):
        cards = []
        for player_pool in self._players_pools:
            for card in player_pool:
                cards.append(card)
        self._clear()
        return cards

    # (Интерйес доступа)
    # Игрок оповещает о взятии карт
    def on_cards_taken(self):
        self._notify(fill_hands=True, what_happened='taken')

    # (Интерфейс доступа)
    # Бито
    def beat_cards(self):
        self._settle()
        self._beaten_alarm()

    def _beat_cards(self):
        for player_pool in self._players_pools:
            for card in player_pool:
                self._beaten.eat(card.info)
        self._clear()
        self._notify(fill_hands=True, what_happened='beaten')

    # Очистить стол
    def _clear(self):
        for player_pool in self._players_pools:
            player_pool.clear()

    def _fill_hands(self):
        if self._deck.size == 0:
            self._notify(fill_hands=False, what_happened='end')
            if self._subscribers[0].cards_count == 0:
                self._alarm.set_text('Победа!')
                self._exit_func()
            elif self._subscribers[1].cards_count == 0:
                self._alarm.set_text('Поражение')
                self._exit_func()
        for sub in self._subscribers:
            if sub.cards_count < 6 and self._deck.size > 0:
                new_cards_count = 6 - sub.cards_count
                if self._deck.size < new_cards_count:
                    new_cards_count = self._deck.size
                new_cards = self._deck.give_cards(new_cards_count)
                sub.fill_hand(new_cards)
        if self._deck.size == 0:
            self._deck.set_invisible()

    def update(self):
        self._deck.update()
        for player_pool in self._players_pools:
            for card in player_pool:
                card.update()
        if self._beat:
            if self._beat_in > 0:
                self._beat_in -= 1
            else:
                self._beat = False
                self._beat_cards()

    def draw(self, surface, dx=0, dy=0):
        self._deck.draw(surface)
        if self._subscribers[0].is_offensive:
            players_pools = self._players_pools
        else:
            players_pools = self._players_pools[::-1]
        for player_pool in players_pools:
            for card in player_pool:
                card.draw(surface)
        self._alarm.draw(surface)

    # Метод, оповещающий подписчиков (игроков) об изменении ситуации на столе
    def _notify(self, fill_hands, what_happened):
        if what_happened == 'begin':
            for sub in self._subscribers:
                if type(sub) is Algo:
                    sub.init()

        if fill_hands:
            self._fill_hands()

        if what_happened == 'beaten':
            self._turn_alarm()

        for i, sub in enumerate(self._subscribers):
            if sub.at_bottom:
                self_info = self.bottom_player_info
                opponent_info = self.top_player_info
            else:
                self_info = self.top_player_info
                opponent_info = self.bottom_player_info
            # opponent_i = (i + 1) % len(self._subscribers)
            # opponent_hand_cards_count = self._subscribers[opponent_i].cards_count

            sub.listen(self_info, opponent_info, what_happened)
