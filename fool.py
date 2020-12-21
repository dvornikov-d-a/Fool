import config as c
from game import Game
from game_objects.button import Button
from game_objects.decision_makers.human.user import User
from game_objects.deck import Deck
from game_objects.hand import Hand
from game_objects.table import Table


class Fool(Game):
    def __init__(self):
        Game.__init__(self, 'Дурак', c.screen_width, c.screen_height, c.menu_background, c.icon, c.frame_rate)
        self._create_main_menu()

    def _create_main_menu(self):
        def on_play_with_algo(button):
            self._start_game('algo')

        def on_play_with_ai(button):
            self._start_game('ai')

        def on_play_online(button):
            self._start_game('online')

        def on_quit(button):
            self._running = False

        self._background_image = c.menu_background
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
            self._objects.append(b)
            self._events_handlers.append(b)

    def _start_game(self, mode):
        self._clear()
        self._background_image = c.game_background

        table = Table()
        bottom_hand = Hand(at_bottom=True)
        top_hand = Hand(at_bottom=False)

        self._objects.append(table)
        self._objects.append(bottom_hand)
        self._objects.append(top_hand)

        if mode == 'algo':
            self._events_handlers.append(bottom_hand)
            self._events_handlers.append(top_hand)

            bottom_player = User(bottom_hand, table, is_offensive=True)
            self._objects.append(bottom_player.finish_turn_button)
            self._events_handlers.append(bottom_player)
            self._events_handlers.append(bottom_player.finish_turn_button)
            top_player = User(top_hand, table, is_offensive=False)
            self._objects.append(top_player.finish_turn_button)
            self._events_handlers.append(top_player)
            self._events_handlers.append(top_player.finish_turn_button)
            table.init_game(bottom_player, top_player)
        elif mode == 'ai':
            pass
        elif mode == 'online':
            pass

