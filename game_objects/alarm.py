import pygame

import config as c
import colors
from game_objects.game_object import GameObject
from game_objects.text_object import TextObject


class Alarm(GameObject):
    def __init__(self, x, y):
        GameObject.__init__(self, x, y, 0, 0,
                            visible=False)
        self._visible_time = c.frame_rate * 2
        self._visible_timing = self._visible_time
        self._text = ''
        self._text_object = TextObject(self.centerx, self.centery, lambda: self._text,
                                       colors.YELLOW1, c.font_name, c.font_size, back_color=colors.BLACK)

    def minus_visible(self):
        self._visible_timing -= 1
        if self._visible_timing == 0:
            self.set_invisible()
            self._visible_timing = self._visible_time

    def set_text(self, text):
        if self._text != text:
            self._text = text
        self.set_visible()

    def draw(self, surface, dx=0, dy=0):
        if self.visible:
            self._text_object.draw(surface, centralized=True)
            self.minus_visible()
