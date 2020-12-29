import pygame
import random

import colors
import config as c
from game_objects.card import Card
from game_objects.game_object import GameObject


# Колода карт
from game_objects.text_object import TextObject


class Deck(GameObject):
    def __init__(self):
        GameObject.__init__(self,
                            c.screen_width - c.card_w - 5,
                            c.screen_height // 2 - c.card_h // 2,
                            c.card_w, c.card_h)
        self._image = pygame.transform.smoothscale(c.flop, (self.width, self.height))
        self._cards = []
        self._fill_deck()
        self._shuffle()
        self._trump_card = self._cards[0]
        self._trump_card.turn_90()
        self._trump_card.show()

        def size_text_func():
            return str(self.size)

        self._size_text = TextObject(self.left + 12, self.top + 5, size_text_func,
                                     colors.YELLOW1, c.font_name, c.font_size, colors.BLACK)

    @property
    def size(self):
        return len(self._cards)

    @property
    def trump(self):
        return self._trump_card.suit
                
    def _fill_deck(self):
        self._cards = []
        for suit in c.suits:
            for nominal in c.nominals:
                card = Card(0, 0, suit, nominal)
                self._cards.append(card)

    def _shuffle(self):
        random.shuffle(self._cards)

    def give_cards(self, count=6):
        given_cards = []
        for i in range(count):
            given_card = self._cards.pop()
            if self.size == 0:
                given_card.turn_90()
            given_cards.append(given_card)
        return given_cards

    def draw(self, surface, dx=0, dy=0):
        if self.visible:
            self._trump_card.draw(surface, self.left - c.card_h // 2, self.top + (c.card_h - c.card_w) // 2)
            surface.blit(self._image, (self.left, self.top))
            self._size_text.draw(surface)
