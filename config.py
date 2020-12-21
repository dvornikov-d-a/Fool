import colors
import pygame


suits = ('clubs', 'diamonds', 'hearts', 'spades')
nominals = ('6', '7', '8', '9', '10', 'jack', 'queen', 'king', 'ace')

screen_width = 1280
screen_height = 720

frame_rate = 100

default_background = colors.GRAY
menu_background = pygame.image.load('source/images/menu_background.jpg')
game_background = pygame.image.load('source/images/game_background.jpg')
icon = pygame.image.load('source/images/game_icon.png')
flop = pygame.image.load('source/images/cards/flop.png')
flop_90 = pygame.image.load('source/images/cards/flop_90.png')
hover_bounds = pygame.image.load('source/images/cards/hover_bounds.png')

button_text_color = colors.WHITESMOKE
button_normal_back_color = colors.BLACK
button_hover_back_color = colors.GRAY
button_pressed_back_color = colors.GRAY

font_name = 'Arial'
font_size = 30

main_menu_offset_x = 20
main_menu_offset_y = 20
main_menu_button_w = 300
main_menu_button_h = 50

card_w = 372 // 4
card_h = 516 // 4

hand_offset_x = 10
hand_offset_y = 10
hand_w = screen_width - card_h // 2
hand_h = card_h + 2 * hand_offset_y
hand_max_int_between_cards = 10

small_menu_width = 300
small_menu_height = 250
