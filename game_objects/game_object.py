from pygame.rect import Rect


class GameObject:
    def __init__(self, x, y, w, h, speed=(0, 0)):
        self._bounds = Rect(x, y, w, h)
        self._speed = speed
    
    @property
    def left(self):
        return self._bounds.left
    
    @property
    def right(self):
        return self._bounds.right

    @property
    def top(self):
        return self._bounds.top

    @property
    def bottom(self):
        return self._bounds.bottom

    @property
    def width(self):
        return self._bounds.width

    @property
    def height(self):
        return self._bounds.height

    @property
    def center(self):
        return self._bounds.center

    @property
    def centerx(self):
        return self._bounds.centerx

    @property
    def centery(self):
        return self._bounds.centery

    def in_bounds(self, pos):
        return self._bounds.collidepoint(pos)

    def draw(self, surface, dx=0, dy=0):
        pass

    def move(self, dx, dy):
        self._bounds = self._bounds.move(dx, dy)

    def update(self):
        pass
