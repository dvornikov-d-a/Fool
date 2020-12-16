import pygame

import config as c
from game_objects.game_object import GameObject
from events_handler import EventsHandler


class Hand(GameObject, EventsHandler):
    def __init__(self, cards, at_bottom):
        self._at_bottom = at_bottom
        if self._at_bottom:
            y = c.screen_height - 2 * c.hand_offset_y - c.card_h
        else:
            y = 0
        GameObject.__init__(self, 0, y, c.hand_w, c.hand_h)
        EventsHandler.__init__(self)
        self._cards = cards
        self._settle()

        self._up_card = None

        # Карта, готовая отправиться на стол.
        self._table_card = None

    def __iter__(self):
        return self._cards.__iter__()

    def __next__(self):
        return self._cards.__next__()

    @property
    def size(self):
        return len(self._cards)

    @property
    def table_card(self):
        return self._table_card

    def hide(self):
        for card in self:
            card.hide()

    def show(self):
        for card in self:
            card.show()

    def _settle(self):
        if self.size > 1:
            int_between = min(c.hand_max_int_between_cards,
                              (self.width - 2 * c.hand_offset_x - self.size * c.card_w) // (self.size - 1))
        else:
            int_between = 0
        offset_x = (self.width - 2 * c.hand_offset_x - self.size * c.card_w - int_between * (self.size - 1)) // 2
        for i, card in enumerate(self):
            card.move(self.left + c.hand_offset_x + offset_x - card.left + int_between * i + c.card_w * i,
                      self.top + c.hand_offset_y - card.top)

    def _get_collided_cards(self, pos):
        return [card for card in self if card.in_bounds(pos)]

    def _focus_on_top_card(self, pos):
        collided_cards = self._get_collided_cards(pos)
        if len(collided_cards) > 0:
            if self._up_card is None:
                self._up_card = collided_cards[-1]
                self._up_card.up()
            else:
                if self._up_card not in collided_cards:
                    self._up_card.down()
                    self._up_card = collided_cards[-1]
                    self._up_card.up()

    def _focus_on_next_card(self, pos):
        collided_cards = self._get_collided_cards(pos)
        if self._up_card is not None and len(collided_cards) > 1:
            self._up_card.down()
            cur_i = collided_cards.index(self._up_card)
            next_i = cur_i - 1
            self._up_card = collided_cards[next_i]
            self._up_card.up()

    def _handle_mouse_motion(self, pos):
        if not any(card for card in self if card.focused):
            self._focus_on_top_card(pos)

    def _handle_mouse_button_down(self, button, pos):
        if button == 3:
            self._focus_on_next_card(pos)

    def _handle_mouse_button_up(self, button, pos):
        if button == 1:
            moved_cards = [card for card in self if card.moved]
            if any(moved_cards):
                table_cards = [card for card in self if not self.in_bounds((card.centerx, card.centery))]
                if any(table_cards):
                    table_card = table_cards[0]
                    table_card.disable()
                    self._cards.remove(table_card)
                    self._table_card = table_card
                self._settle()
                for card in moved_cards:
                    card.settled()
            self._focus_on_top_card(pos)

    def handle_events(self, events):
        EventsHandler.handle_events(self, events)
        for card in self:
            card.handle_events(events)

    def update(self):
        for card in self:
            card.update()
        if self._table_card is not None:
            self._table_card.update()

    def draw(self, surface):
        for card in [card for card in self if card.state == 'normal']:
            card.draw(surface)
        for card in [card for card in self if card.state == 'hover']:
            card.draw(surface)
        for card in [card for card in self if card.state == 'selected']:
            card.draw(surface)
        if self._table_card is not None:
            self._table_card.draw(surface)