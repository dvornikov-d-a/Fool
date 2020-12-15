import pygame


class TextObject:
    def __init__(self, x, y, text_func, color, font_name, font_size):
        self._pos = (x, y)
        self._text_func = text_func
        self._color = color
        self._font = pygame.font.SysFont(font_name, font_size)
        self._bounds = self.get_surface(text_func())

    def draw(self, surface, centralized=False):
        text_surface, self._bounds = self.get_surface(self._text_func())
        if centralized:
            pos = (self._pos[0] - self._bounds.width // 2,
                   self._pos[1])
        else:
            pos = self._pos
        surface.blit(text_surface, pos)
        
    def get_surface(self, text):
        text_surface = self._font.render(text,
                                         False,
                                         self._color)
        return text_surface, text_surface.get_rect()

    def update(self):
        pass
