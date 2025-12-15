import pygame
from enum import Enum

from constants import SCREEN_SIZE, BG_BLUE
from GameObjects.game_manager import GameManager
from GameObjects.main_menu import MainMenu

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
running = True
clock = pygame.time.Clock()
delta_time = 0.1

pygame.mixer.init()

o_GameManager : GameManager
main_menu = MainMenu()

#region GameState stuff
class GameState(Enum):
     MAIN_MENU = 0
     GAME = 1

curr_game_state = GameState.MAIN_MENU

def switching_game_state(game_state_to: GameState, game_state_from: GameState):
     global curr_game_state
     curr_game_state = game_state_to

     # From
     match (game_state_from):
          case GameState.MAIN_MENU: main_menu.switching_from()

     # To
     match (game_state_to):
          case GameState.MAIN_MENU: main_menu.switching_to()
#endregion

while running:
    event = pygame.event.get()

    if curr_game_state == GameState.MAIN_MENU:
        main_menu.update(screen, event)
        running = not main_menu.quit_game_flag
        if main_menu.song_selected_flag:
            # Get song JSON path
            chart_path = main_menu.get_chart()

            # Set up the Game Manager
            switching_game_state(GameState.GAME, GameState.MAIN_MENU)
            o_GameManager = GameManager(chart_path)
    elif curr_game_state == GameState.GAME:
        o_GameManager.update(screen, event, delta_time)
        if o_GameManager.o_ScoreScreen.flag_leave_score_screen == True:
             switching_game_state(GameState.MAIN_MENU, GameState.GAME)
             o_GameManager = None

    for event in event:
          if event.type == pygame.QUIT:
               running = False
    
    pygame.display.flip() #Tells pygame we're done rendering
    delta_time = clock.tick(60) / 1000
    delta_time = max(0.001, min(0.1, delta_time))
    screen.fill(BG_BLUE) #Clear the screen for the next render loop


pygame.mixer.music.unload()
pygame.quit()
