import random

import config as c
from game_objects.deck import Deck
from game_objects.game_object import GameObject
from game_objects.beaten import Beaten


class Table(GameObject):
    def __init__(self):
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

    @property
    def trump(self):
        return self._trump

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

    @property
    def _size(self):
        return max(len(self._players_pools[0]), len(self._players_pools[1]))

    def init_game(self, bottom_player, top_player):
        bottom_player.fill_hand(self._deck.give_cards(count=6))
        top_player.fill_hand(self._deck.give_cards(count=6))
        self._notify()

    def _settle(self):
        if self._size < 2:
            int_between = 0
        else:
            int_between = min(c.hand_max_int_between_cards,
                              (self.width - 2 * c.hand_offset_x - self._size * c.card_w) // (self._size - 1))
        offset_x = (self.width - 2 * c.hand_offset_x - self._size * c.card_w - int_between * (self._size - 1)) // 2
        for i, card in enumerate(self._players_pools[0]):
            card.move(self.left + c.hand_offset_x + offset_x - card.left + int_between * i + c.card_w * i,
                      self.top + self.height // 2 + c.hand_offset_y - card.top)
        for i, card in enumerate(self._players_pools[1]):
            card.move(self.left + c.hand_offset_x + offset_x - card.left + int_between * i + c.card_w * i,
                      self.bottom + c.card_h + c.hand_offset_y - card.top)

    def _get_player_info(self, player_pool):
        player_info = []

        for i in range(self._size):
            if i < len(player_pool):
                card = player_pool[i]
                player_card_info = card.info
            else:
                player_card_info = ('', '')

            player_info.append(player_card_info)

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

    # (Интерфейс доступа)
    # Отдать карты на столе
    def give_all_cards(self):
        cards = []
        for player_pool in self._players_pools:
            for card in player_pool:
                cards.append(card)
        self._clear()
        return cards

    # (Интерфейс доступа)
    # Бито
    def beat_cards(self):
        for player_pool in self._players_pools:
            for card in player_pool:
                self._beaten.eat(card.info)
        self._clear()
        for sub in self._subscribers:
            if sub.cards_count < 6:
                new_cards_count = 6 - sub.cards_count
                new_cards = self._deck.give_cards(new_cards_count)
                sub.fill_hand(new_cards)

    # Очистить стол
    def _clear(self):
        for player_pool in self._players_pools:
            for card in player_pool:
                player_pool.remove(card)

    def update(self):
        for player_pool in self._players_pools:
            for card in player_pool:
                card.update()

    def draw(self, surface):
        for player_pool in self._players_pools:
            for card in player_pool:
                card.draw(surface)

    # Метод, оповещающий подписчиков (игроков) об изменении ситуации на столе
    def _notify(self):
        for i, sub in enumerate(self._subscribers):
            if sub.at_bottom:
                self_info = self.bottom_player_info
                opponent_info = self.top_player_info
            else:
                self_info = self.top_player_info
                opponent_info = self.bottom_player_info
            opponent_i = (i + 1) % len(self._subscribers)
            opponent_hand_cards_count = self._subscribers[opponent_i].cards_count

            sub.listen(self_info, opponent_info, opponent_hand_cards_count)


