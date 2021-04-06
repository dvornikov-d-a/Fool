import copy

import config as c
from game_objects.decision_makers.player import Player


class Algo(Player):
    def __init__(self, hand, table, is_offensive):
        super().__init__(hand, table, is_offensive)

        # Список словарей вида {'suit': '', 'nominal': ''}
        self._all_cards = []
        for suit in c.suits:
            for nominal in c.nominals:
                self._all_cards.append({'suit': suit, 'nominal': nominal})

        # Список словарей вида {'suit': '', 'nominal': ''}
        self._cards_in_game = copy.deepcopy(self._all_cards)

        # Близость конца игры -- коэффициент мю
        # (доля карт, вышедших из колоды)
        self._mu = 0

        # Список словарей вида {'suit': '', 'nominal': ''}
        self._beaten_info = []
        # Список словарей вида {'suit': '', 'nominal': '', 'rel-power': 0-1, 'P-power': 0-1}
        self._self_hand_power = []

        # Список словарей вида {'suit': '', 'nominal': ''}
        self._opponent_hand_info = []
        # Список словарей вида {'suit': '', 'nominal': ''}
        # от нижней (козыря) к верхней (неизвестной)
        self._deck_info = []

        # Информация о последнем состоянии карт "на столе"
        # Список словарей вида {'suit': '', 'nominal': ''}
        self._last_self_table_info = []
        self._last_opponent_table_info = []

    # Принимает список кортежей, в которых 1й элемент - масть, а 2й - номинал.
    # Возращает список словарей вида {'suit': '', 'nominal': ''}.
    def _get_beautiful_cards_info(self, list_of_tuples):
        list_of_dicts = []
        for tuple_ in list_of_tuples:
            dict_ = self._get_beautiful_card_info(tuple_)
            list_of_dicts.append(dict_)
        return list_of_dicts

    @staticmethod
    def _get_beautiful_card_info(tuple_):
        return {'suit': tuple_[0], 'nominal': tuple_[1]}

    @property
    def _self_hand_info(self):
        return self._get_beautiful_cards_info(self._hand.cards_info)

    @property
    def _actual_self_table_info(self):
        return self._get_beautiful_cards_info(self._self_info)

    @property
    def _actual_opponent_table_info(self):
        return self._get_beautiful_cards_info(self._opponent_info)

    @property
    def _last_table_info(self):
        return self._last_self_table_info + self._last_opponent_table_info

    @property
    def _actual_table_info(self):
        return self._actual_self_table_info + self._actual_opponent_table_info

    @property
    def _unknown_cards_in_game(self):
        return [card for card in self._cards_in_game if (card not in self._self_hand_info)
                and (card not in self._actual_table_info)
                and (card not in self._deck_info)
                and (card not in self._opponent_hand_info)]

    def _factorial(self, n):
        if n < 0:
            return -1

        if n == 1 or n == 0:
            return 1
        else:
            return n * self._factorial(n - 1)

    def _combination_count(self, k, n):
        if n > 0 and 1 <= k <= n:
            return self._factorial(n) / (self._factorial(k) * self._factorial(n - k))
        else:
            return -1

    def _opponent_has_any_from_group_probability(self, in_group_unknown_count):
        if in_group_unknown_count == 0:
            return 0

        in_deck_unknown_count = len([card for card in self._deck_info if card['suit'] == '' or card['nominal'] == 0])
        if in_group_unknown_count > in_deck_unknown_count:
            # Не помещаются в колоду
            return 1

        if 1 <= in_group_unknown_count <= in_deck_unknown_count:
            in_game_unknown_count = len(self._unknown_cards_in_game)
            return round(1 - self._combination_count(in_deck_unknown_count - in_group_unknown_count,
                                                     in_game_unknown_count - in_group_unknown_count) /
                         self._combination_count(in_deck_unknown_count,
                                                 in_game_unknown_count), 2)
        else:
            return 0

    def _on_table_event(self, what_happened):
        if what_happened == 'begin':
            pass
        elif what_happened == 'placed':
            if self._opponent_cards_count < len(self._opponent_hand_info):
                # Карту положил на стол противник (актуальное количество карт на руках у противника стало меньше)
                new_card = self._actual_opponent_table_info[-1]
                if new_card in self._opponent_hand_info:
                    # Алгоритм знал о наличии карты у противника
                    self._opponent_hand_info.remove(new_card)
                else:
                    # Алгоритм не знал о наличии карты у противника
                    self._opponent_hand_info.remove({'suit': '', 'nominal': ''})
            else:
                # Карту положил на стол сам алгоритм
                # Все необходимые изменения -- ниже
                pass
        elif what_happened == 'beaten':
            # Запомнить то, что в бите
            self._beaten_info += self._last_table_info
            self._mu = round((len(self._beaten_info) + len(self._hand.cards) + self._opponent_cards_count)
                             / len(self._all_cards), 2)

            self._if_opponent_hand_filled()

        elif what_happened == 'taken':
            if self._is_offensive:
                # Карты берёт противник
                self._opponent_hand_info += self._last_table_info

            self._if_opponent_hand_filled()

        elif what_happened == 'end':
            return

        self._last_self_table_info = self._actual_self_table_info
        self._last_opponent_table_info = self._actual_opponent_table_info

        unknown_cards = self._unknown_cards_in_game
        if any(unknown_cards):
            # Если остались карты, чьё местоположение неизвестно...
            if {'suit': '', 'nominal': ''} not in self._deck_info:
                # ... и они -- не в колоде,
                # а значит -- у противника
                for card in self._opponent_hand_info:
                    if card == {'suit': '', 'nominal': ''}:
                        known = unknown_cards.pop()
                        card['suit'] = known['suit']
                        card['nominal'] = known['nominal']
            elif {'suit': '', 'nominal': ''} not in self._opponent_hand_info:
                # ... и они -- не у противника,
                # а значит -- в колоде
                if len(unknown_cards) == 1:
                    # Это всего одна карта
                    self._deck_info[-1] = unknown_cards.pop()

        self._self_hand_power = []
        for card in copy.deepcopy(self._self_hand_info):
            card['rel-power'] = self._calc_rel_power(card)
            card['P-power'] = self._calc_prob_power(card)
            self._self_hand_power.append(card)

    def _calc_weaker_count(self, card):
        n_weaker = 0
        for other in self._cards_in_game:
            if self._first_beats_second(card, other):
                n_weaker += 1
        return n_weaker

    def _calc_rel_power(self, card):
        if len(self._cards_in_game) > 0:
            n_weaker = self._calc_weaker_count(card)
            return round(n_weaker / len(self._cards_in_game), 2)
        else:
            return 0

    def _calc_weaker_unknown_count(self, card):
        n_weaker = 0
        for other in self._unknown_cards_in_game:
            if self._first_beats_second(card, other):
                n_weaker += 1
        return n_weaker

    def _calc_prob_power(self, card):
        return self._opponent_has_any_from_group_probability(self._calc_weaker_unknown_count(card))

    def _first_beats_second(self, first, second):
        if first['suit'] == second['suit']:
            if self.nominals_scores[first['nominal']] > self.nominals_scores[second['nominal']]:
                return True
            else:
                return False
        else:
            if first['suit'] == self.trump:
                return True
            else:
                return False

    def _if_opponent_hand_filled(self):
        new_opponent_cards_count = self._opponent_cards_count - len(self._opponent_hand_info)
        if new_opponent_cards_count > 0:
            # Противнику были розданы карты
            for i in range(new_opponent_cards_count):
                new_card = self._deck_info.pop()
                self._opponent_hand_info.append(new_card)

    def _calc_opponent_has_suit_probability(self, attack_card_suit):
        if attack_card_suit in set([card['suit'] for card in self._opponent_hand_info]):
            return 1
        else:
            ofsuit_count = len([card for card in self._unknown_cards_in_game if card['suit'] == attack_card_suit])
            return self._opponent_has_any_from_group_probability(ofsuit_count)

    def fill_hand(self, new_cards):
        self._if_opponent_hand_filled()
        Player.fill_hand(self, new_cards)
        # ToDo
        # Убрать после отладки
        self.show_hand()
        for i in range(len(new_cards)):
            self._deck_info.pop()

    def init(self):
        if len(self._deck_info) == 0:
            # Запомнить козырную карту в колоде
            trump_card_info = self._get_beautiful_card_info(self._table.trump_info)
            self._deck_info.append(trump_card_info)
            for i in range(len(self._all_cards) - 1):
                unknown_card = {'suit': '', 'nominal': ''}
                self._deck_info.append(unknown_card)

    def _attack(self, power_type):
        twin_card = {'i': -1, power_type: 1.1}
        suit_opponent_miss_card = {'i': -1, power_type: 1.1}
        min_rel_power_card = {'i': -1, power_type: 1.1}
        # Здесь карта - отображаемый игровой объект, а не кортеж "масть-номинал"
        for i, card_object in enumerate(self._hand):
            if card_object in self._available_decisions:
                power = self._self_hand_power[i][power_type]
                if power < min_rel_power_card[power_type]:
                    min_rel_power_card['i'] = i
                    min_rel_power_card[power_type] = power
                if power < 0.5:
                    if [card.nominal for card in self._available_decisions].count(card_object.nominal) > 1:
                        if power < twin_card[power_type]:
                            twin_card['i'] = i
                            twin_card[power_type] = power
                    if self._calc_opponent_has_suit_probability(card_object.suit) == 0:
                        if power < suit_opponent_miss_card[power_type]:
                            suit_opponent_miss_card['i'] = i
                            suit_opponent_miss_card[power_type] = power

        if power_type == 'rel-power':
            power_bound = 0.5
        else:
            power_bound = 0.7
        # Если карту желательно оставить и есть такая возможность
        if min_rel_power_card[power_type] >= power_bound and len(self._self_info) > 0:
            return lambda: self._table.beat_cards()

        if twin_card['i'] != -1 or suit_opponent_miss_card['i'] != -1:
            if twin_card[power_type] <= suit_opponent_miss_card[power_type]:
                table_card_i = twin_card['i']
            else:
                table_card_i = suit_opponent_miss_card['i']
            table_card = self._hand.give_card_by_i(table_card_i)
        else:
            table_card = self._hand.give_card_by_i(min_rel_power_card['i'])
        return lambda: self._table.put_card(table_card, self.at_bottom)

    def _defense(self, power_type):
        min_rel_power_card = {'i': -1, power_type: 1.1}
        # Здесь карта - отображаемый игровой объект, а не кортеж "масть-номинал"
        for i, card_object in enumerate(self._hand):
            if card_object in self._available_decisions:
                power = self._self_hand_power[i][power_type]
                if power < min_rel_power_card[power_type]:
                    min_rel_power_card['i'] = i
                    min_rel_power_card[power_type] = power
        if min_rel_power_card[power_type] <= 0.9 or power_type == 'P-power':
            table_card = self._hand.give_card_by_i(min_rel_power_card['i'])
            return lambda: self._table.put_card(table_card, self.at_bottom)
        else:
            return lambda: self._take_all_cards(), self._table.on_cards_taken()

    def _make_decision(self):
        if len(self._unknown_cards_in_game) != 0:
            # Известно местоположение не всех карт - исход партии трудновычислим
            if self._mu < 0.8:
                if self.is_offensive:
                    decision = self._attack('rel-power')
                else:
                    decision = self._defense('rel-power')
            else:
                if self.is_offensive:
                    decision = self._attack('P-power')
                else:
                    decision = self._defense('P-power')
        else:
            # Известно местоположение всех карт - исход партии может быть вычислен
            # ToDo
            # Написать алгоритм обхода дерева решений
            if self._mu < 0.8:
                if self.is_offensive:
                    decision = self._attack('rel-power')
                else:
                    decision = self._defense('rel-power')
            else:
                if self.is_offensive:
                    decision = self._attack('P-power')
                else:
                    decision = self._defense('P-power')
        return decision

    def react(self):
        self._make_decision()()
