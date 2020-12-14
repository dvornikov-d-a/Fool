import pygame

import config as c
from game_objects.game_object import GameObject
from game_objects.text_object import TextObject
from events_handler import EventsHandler


class Button(GameObject, EventsHandler):
    def __init__(self, x, y, w, h, text, on_click=lambda x: None, padding=0):
        super().__init__(x, y, w, h)
        self.state = 'normal'
        self.on_click = on_click

        self.text = TextObject(x + padding, y + padding, lambda: text,
                               c.button_text_color, c.font_name, c.font_size)

    @property
    def back_color(self):
        return dict(normal=c.button_normal_back_color,
                    hover=c.button_hover_back_color,
                    pressed=c.button_pressed_back_color)[self.state]

    def _handle_mouse_motion(self, pos):
        if self.bounds.collidepoint(pos):
            if self.state != 'pressed':
                self.state = 'hover'
        else:
            self.state = 'normal'

    def _handle_mouse_button_down(self, button, pos):
        if self.bounds.collidepoint(pos):
            if button == 1:
                self.state = 'pressed'

    def _handle_mouse_button_up(self, button, pos):
        if self.bounds.collidepoint(pos):
            if button == 1:
                if self.state == 'pressed':
                    self.on_click(self)
                    self.state = 'hover'

    def draw(self, surface):
        pygame.draw.rect(surface,
                         self.back_color,
                         self.bounds)
        self.text.draw(surface)
