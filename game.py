import pygame
import sys

from events_handler import EventsHandler


class Game(EventsHandler):
    def __init__(self, caption, width, height, back_image, icon, frame_rate):
        EventsHandler.__init__(self)
        self._background_image = back_image
        self._icon = icon
        self._frame_rate = frame_rate
        self._game_over = False
        self._running = True
        self._objects = []
        self._events_handlers = []

        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.font.init()

        self._surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)

        pygame.display.set_icon(self._icon)

        self._clock = pygame.time.Clock()

    def _clear(self):
        self._objects = []
        self._events_handlers = []

    def update(self):
        for o in self._objects:
            o.update()
        
    def draw(self):
        for o in self._objects:
            o.draw(self._surface)

    def get_and_handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self._running = False
        self.handle_events(events)
        for events_handler in self._events_handlers:
            events_handler.handle_events(events)

    def run(self):
        while self._running:
            self._surface.blit(self._background_image, (0, 0))

            self.get_and_handle_events()
            self.update()
            self.draw()

            pygame.display.update()
            self._clock.tick(self._frame_rate)

        pygame.quit()
        sys.exit()
