import time

from game_objects.game_object import GameObject


class Player:
    def __init__(self, hand, table, is_offensive):
        self._hand = hand
        self._table = table
        # Роль: нападающий/защищающийся.
        self._is_offensive = is_offensive

        # Список карт, которыми принял решение ходить игрок.
        self._decision = []

    # Метод, вызываемый экземпляром Стола
    def change_role(self):
        self._is_offensive = not self._is_offensive

    # Метод, вызываемый экземпляром Стола в ответ на изменение ситуации и
    # провоцирующий изменения ситуации на столе.
    def listen(self, self_info, opponent_info, opponent_cards_count):
        available_decisions = self._calc_available_decisions(self_info, opponent_info, opponent_cards_count)
        # Есть доступные решения
        if available_decisions:
            self.react(self_info, opponent_info, opponent_cards_count, available_decisions)
        # Нет доступных решений
        else:
            # Равное кол-во карт с обоих сторон
            if len(self_info) == len(opponent_info):
                # Нападающий
                if self._is_offensive:
                    # Завершение атаки -> Бито
                    self._table.beat_cards()
                # Отбивающийся
                else:
                    # Ожидание атаки
                    self._wait()
            # Неравное кол-во карт
            else:
                # Нападающий
                if self._is_offensive:
                    # Ожидание защиты
                    self._wait()
                # Отбивающийся
                else:
                    # Атаку невозможно отбить -> взять карты
                    self._take_all_cards()
                    self._table.on_cards_taken()

    def _wait(self):
        pass

    # Метод, вызываемый экземпляром Стола
    def fill_hand(self, new_cards):
        self._hand.take_cards(new_cards)

    @property
    def nominals_scores(self):
        return self._table.nominals_scores

    @property
    def trump(self):
        return self._table.trump

    @property
    def at_bottom(self):
        return self._hand.at_bottom

    @property
    def is_offensive(self):
        return self._is_offensive

    @property
    def cards_count(self):
        return self._hand.size

    # Переопределяется в классе-наследнике
    def react(self, self_info, opponent_info, opponent_cards_count, available_decisions):
        pass

    def _take_all_cards(self):
        taken_cards = self._table.give_all_cards()
        self._hand.take_cards(taken_cards)
        self._table.on_cards_taken()

    def _give_cards(self, cards):
        given_cards = self._hand.give_cards(cards)
        return given_cards

    # Расчёт возможных ходов
    def _calc_available_decisions(self, self_info, opponent_info, opponent_cards_count):
        table_info = (self_info, opponent_info)
        # Пустой стол
        if table_info == ((), ()):
            # Наступающий
            if self._is_offensive:
                # Можно ходить любой картой
                return self._hand.cards
            # Отбивающийся
            else:
                # Нет доступных решений
                return []

        # Непустой стол
        available_decisions = []

        if self._is_offensive:
            # Нападающий
            if len(self_info) == len(opponent_info):
                # Соперник успешно отбился -> поиск новых ходов
                all_nominals_on_table = set([card_info[1] for card_info in self_info + opponent_info])
                if not any(all_nominals_on_table):
                    available_decisions += self._hand.cards
                else:
                    for my_card in self._hand:
                        # Можно сходить любой картой уже имеющегося номинала на столе
                        if my_card.nominal in all_nominals_on_table:
                            available_decisions.append(my_card)
            else:
                # Соперник думает -> поиск "близнеца" последней подкинутой карты карты
                last_card = self_info[-1]
                available_decisions += self._find_twins(last_card)
        # Отбивающийся
        else:
            # Есть карты, которые нужно отбить
            if len(opponent_info) > len(self_info):
                # Первая неотбитая
                attack_card = opponent_info[len(self_info)]
                available_decisions += self._find_cards_stronger_then(attack_card)
            # Нет карт, которые нужно отбить
            else:
                # Режим ожидания
                self._wait()

        return available_decisions

    def _find_twins(self, card_info):
        twins = []
        for my_card in self._hand:
            if my_card.nominal == card_info[1]:
                twins.append(my_card)
        return twins

    def _find_cards_stronger_then(self, card_info):
        relevant_cards = []
        for my_card in self._hand:
            if self._first_is_stronger(my_card.info, card_info):
                relevant_cards.append(my_card)
        return relevant_cards

    def _first_is_stronger(self, first_card_info, second_card_info):
        first_suit, first_nominal = first_card_info
        second_suit, second_nominal = second_card_info
        if first_suit == self.trump \
                and second_suit != self.trump:
            return True

        if second_suit == self.trump \
                and first_suit != self.trump:
            return False

        if first_suit != second_suit:
            return False

        first_nominal_score = self.nominals_scores[first_nominal]
        second_nominal_score = self.nominals_scores[second_nominal]
        if first_nominal_score > second_nominal_score:
            return True
        else:
            return False

    def hide_hand(self):
        self._hand.hide()

    def show_hand(self):
        self._hand.show()
