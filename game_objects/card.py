import pygame

import config as c
from game_objects.game_object import GameObject
from events_handler import EventsHandler


class Card(GameObject, EventsHandler):
    def __init__(self, x, y, suit, nominal):
        GameObject.__init__(self, x, y, c.card_w, c.card_h)
        EventsHandler.__init__(self)

        self._hidden = True
        self._below = False
        self._state = 'normal'
        self._dest_point = (self.left, self.top)
        self._cur_point = (self.left, self.top)
        self._suit = suit
        self._nominal = nominal

        image_path = 'source/images/cards/' + self._suit + '/' + self._nominal + '.png'
        image = pygame.image.load(image_path)
        self.image = pygame.transform.smoothscale(image, (c.card_w, c.card_h))
        self.flop = pygame.transform.smoothscale(c.flop, (c.card_w, c.card_h))
        self.hover_bounds = pygame.transform.smoothscale(c.hover_bounds, (c.card_w, c.card_h))

    @property
    def info(self):
        return self._suit, self._nominal

    @ property
    def focused(self):
        if self._state == 'hover' or self._state == 'selected':
            return True
        else:
            return False

    def _handle_mouse_motion(self, pos):
        if self._state == 'selected':
            self._dest_point = pos
        elif self._state == 'normal' and self.in_bounds(pos) and not self._below:
            self._state = 'hover'
        elif self._state == 'hover' and (not self.in_bounds(pos) or self._below):
            self._state = 'normal'

    def _handle_mouse_button_down(self, button, pos):
        if button == 1:
            if self.bounds.collidepoint(pos):
                if self._state == 'hover':
                    self._state = 'selected'
                    self._cur_point = pos
                    self._dest_point = pos

    def _handle_mouse_button_up(self, button, pos):
        if button == 1:
            if self.bounds.collidepoint(pos):
                if self._state == 'selected':
                    self._state = 'hover'

    # (Интерфейс управления видимостью лицевой стороны)
    def show(self):
        self._hidden = False

    # (Интерфейс управления видимостью лицевой стороны)
    def hide(self):
        self._hidden = True

    # (Интерфейс управления "уровнем" относительно другой карты)
    def up(self):
        self._below = False

    # (Интерфейс управления "уровнем" относительно другой карты)
    def down(self):
        self._below = True
        self._state = 'normal'

    # Дезактивация + возвращение нормальное состояние
    def disable(self):
        EventsHandler.disable(self)
        self._state = 'normal'

    def update(self):
        if self._cur_point != self._dest_point:
            dx = self._dest_point[0] - self._cur_point[0]
            dy = self._dest_point[1] - self._cur_point[1]
            self.move(dx, dy)
            self._cur_point = self._dest_point

    def draw(self, surface):
        if self._hidden:
            surface.blit(self.flop, (self.left, self.top))
        else:
            surface.blit(self.image, (self.left, self.top))
            if self.focused:
                surface.blit(self.hover_bounds, (self.left, self.top))
