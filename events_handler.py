import pygame


class EventsHandler:
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_button_down(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self._handle_mouse_button_up(event.button, event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_key_down(event.key, event.pos)
            elif event.type == pygame.KEYUP:
                self._handle_key_up(event.key, event.pos)

    # Все нижеперечисленные обработчики событий индивидуальны для каждого игрового объекта
    # и конкретизируются в наследуемом классе

    def _handle_mouse_motion(self, pos):
        pass

    def _handle_mouse_button_down(self, button, pos):
        pass

    def _handle_mouse_button_up(self, button, pos):
        pass

    def _handle_key_down(self, key, pos):
        pass

    def _handle_key_up(self, key, pos):
        pass
