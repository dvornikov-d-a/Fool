import pygame

import config as c
from game_objects.game_object import GameObject
from game_objects.text_object import TextObject
from events_handler import EventsHandler


class Button(GameObject, EventsHandler):
    def __init__(self, x, y, w, h, text, on_click=lambda x: None, padding=0, active=True):
        GameObject.__init__(self, x, y, w, h)
        EventsHandler.__init__(self, active)

        self._state = 'normal'
        self._on_click = on_click
        self._text = TextObject(x + padding, y + padding, lambda: text,
                                c.button_text_color, c.font_name, c.font_size)

    @property
    def back_color(self):
        return dict(normal=c.button_normal_back_color,
                    hover=c.button_hover_back_color,
                    pressed=c.button_pressed_back_color)[self._state]

    def _handle_mouse_motion(self, pos):
        if self.in_bounds(pos):
            if self._state != 'pressed':
                self._state = 'hover'
        else:
            self._state = 'normal'

    def _handle_mouse_button_down(self, button, pos):
        if self.in_bounds(pos):
            if button == 1:
                self._state = 'pressed'

    def _handle_mouse_button_up(self, button, pos):
        if self.in_bounds(pos):
            if button == 1:
                if self._state == 'pressed':
                    self._on_click(self)
                    self._state = 'hover'

    def disable(self):
        EventsHandler.disable(self)
        self._state = 'normal'

    def draw(self, surface, dx=0, dy=0):
        pygame.draw.rect(surface,
                         self.back_color,
                         self._bounds)
        self._text.draw(surface)
