import pygame
import random

import config as c
from game_objects.card import Card
from game_objects.game_object import GameObject


# Колода карт
class Deck(GameObject):
    def __init__(self):
        GameObject.__init__(self,
                            c.screen_width - c.card_h // 2,
                            c.screen_height // 2 - c.card_w // 2,
                            c.card_h, c.card_w)
        self._image = pygame.transform.scale(c.flop_90, (self.width, self.height))
        self._cards = []
        self._fill_deck()
        self._shuffle()

    @property
    def size(self):
        return len(self._cards)
                
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
            given_cards.append(self._cards.pop())
        return given_cards

    def draw(self, surface):
        surface.blit(self._image, (self.left, self.top))
