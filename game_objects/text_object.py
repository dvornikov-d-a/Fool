import pygame


class TextObject:
    def __init__(self, x, y, text_func, color, font_name, font_size, back_color=None):
        self._pos = (x, y)
        self._text_func = text_func
        self._color = color
        self._font = pygame.font.SysFont(font_name, font_size)
        self._bounds = self.get_surface(text_func())
        self._back_color = back_color

    def draw(self, surface, centralized=False):
        text_surface, self._bounds = self.get_surface(self._text_func())
        if centralized:
            pos = (self._pos[0] - self._bounds.width // 2,
                   self._pos[1])
        else:
            pos = self._pos
        if self._back_color is not None:
            ext = 8
            rect = pygame.Rect(pos[0] - ext, pos[1], self._bounds.width + 2 * ext, self._bounds.height)
            pygame.draw.rect(surface,
                             self._back_color,
                             rect)
        surface.blit(text_surface, pos)
        
    def get_surface(self, text):
        text_surface = self._font.render(text,
                                         False,
                                         self._color)
        return text_surface, text_surface.get_rect()

    def update(self):
        pass
