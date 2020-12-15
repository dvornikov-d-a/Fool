import config as c
from game import Game
from game_objects.button import Button


class Fool(Game):
    def __init__(self):
        Game.__init__(self, 'Дурак', c.screen_width, c.screen_height, c.menu_background, c.icon, c.frame_rate)
        self.create_main_menu()

    def create_main_menu(self):
        def on_play_with_algo(button):
            self.start_game('algo')

        def on_play_with_ai(button):
            self.start_game('ai')

        def on_play_online(button):
            self.start_game('online')

        def on_quit(button):
            self.running = False

        self.background_image = c.menu_background
        for i, (text, click_handler) in enumerate((('Играть с алгоритмом', on_play_with_algo),
                                                   ('Играть с ИИ', on_play_with_ai),
                                                   ('Играть по сети', on_play_online),
                                                   ('Выйти', on_quit))):
            b = Button(c.main_menu_offset_x,
                       c.main_menu_offset_y + (c.main_menu_button_h + 5) * i,
                       c.main_menu_button_w,
                       c.main_menu_button_h,
                       text,
                       click_handler,
                       padding=5)
            self.objects.append(b)
            self.events_handlers.append(b)

    def start_game(self, mode):
        self._clear()
        self.background_image = c.game_background
        if mode == 'algo':
            pass
        elif mode == 'ai':
            pass
        elif mode == 'online':
            pass
        pass

