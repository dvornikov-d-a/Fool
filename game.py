import pygame
import sys

from events_handler import EventsHandler


class Game(EventsHandler):
    def __init__(self, caption, width, height, back_image, icon, frame_rate):
        self.background_image = back_image
        self.icon = icon
        self.frame_rate = frame_rate
        self.game_over = False
        self.running = True
        self.objects = []
        self.events_handlers = []

        pygame.mixer.pre_init(44100, 16, 2, 4096)
        pygame.init()
        pygame.font.init()

        self.surface = pygame.display.set_mode((width, height))
        pygame.display.set_caption(caption)

        pygame.display.set_icon(self.icon)

        self.clock = pygame.time.Clock()

    def _clear(self):
        self.objects = []
        self.events_handlers = []

    def update(self):
        for o in self.objects:
            o.update()
        
    def draw(self):
        for o in self.objects:
            o.draw(self.surface)

    def get_and_handle_events(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
        self.handle_events(events)
        for events_handler in self.events_handlers:
            events_handler.handle_events(events)

    def run(self):
        while self.running:
            self.surface.blit(self.background_image, (0, 0))

            self.get_and_handle_events()
            self.update()
            self.draw()

            pygame.display.update()
            self.clock.tick(self.frame_rate)

        pygame.quit()
        sys.exit()
