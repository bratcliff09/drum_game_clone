# Handles the main menu

import pygame
from constants import SCREEN_SIZE, COL_WHITE, COL_YELLOW, COL_NOTE_BLUE, COL_NOTE_RED, NOTE_RADIUS
import json
from Utils.cool_maths import loop
from Utils.page_elements import Text
from os import walk

class MainMenu():
    def __init__(self):
        self.page_num = 0
        # 0 - Start, 1 - Song Selection, 2 - Instructions
        
        #region Main Menu
        self.title_menu_item = 0
        self.title_menu_item_max = 2

        self.txt_title = Text('Drum Game Clone', (0, 0), 
                                   35, (SCREEN_SIZE[1] * 0.5) - 125, 90)
        self.txt_title_start = Text("START", self.txt_title.pos, 0, 150, 30)
        self.txt_title_instructions = Text("INSTRUCTIONS", self.txt_title.pos, 0, 170, 30)
        self.txt_title_exit = Text("EXIT", self.txt_title.pos, 0, 190, 30)

        self.title_font = pygame.font.Font(None, size=90)
        self.font = pygame.font.Font(None, size=30)
        self.font_center = pygame.font.Font(None, size=30)
        self.font_center.align = pygame.FONT_CENTER
        #endregion        

        #region Song Selection
        self.songs_arr = []
        #   {wave_path, chart_path, name, subtitle, artist, demostart}
        self.hi_scores_arr = []
        #   score of index 0 is associated with song of index 0 in songs_arr
        self.selection_menu_item = 0
        self.is_songs_loading = False
        self.init_songs("./Songs")

        self.new_song_selected = True

        self.rect_song = pygame.Rect(SCREEN_SIZE[0] * 0.5 - 200, SCREEN_SIZE[1] * 0.5 - 50, 400, 105)

        self.txt_song_title = Text("", (self.rect_song.x, self.rect_song.y), 25, 10, 30)
        self.txt_song_subtitle = Text("", (self.rect_song.x, self.rect_song.y), 50, 30, 30)
        self.txt_song_artist = Text("", (self.rect_song.x, self.rect_song.y), 50, 50, 30)
        self.txt_score = Text("", (self.rect_song.x, self.rect_song.y), 50, 80, 30)

        self.gui_tri_up_points = [(self.rect_song.centerx - 25, self.rect_song.top - 30), 
                                  (self.rect_song.centerx, self.rect_song.top - 50),
                                  (self.rect_song.centerx + 25, self.rect_song.top - 30)]
        self.gui_tri_bottom_points = [(self.rect_song.centerx - 25, self.rect_song.bottom + 60), 
                                  (self.rect_song.centerx, self.rect_song.bottom + 50 + 30),
                                  (self.rect_song.centerx + 25, self.rect_song.bottom + 60)]
        #endregion

        #region Instructions
        self.txt_instructions_title = Text('Instructions', (0, 0), 
                                   35, (SCREEN_SIZE[1] * 0.5) - 125, 90)
        self.txt_instructions_1 = Text("D K for blue notes", self.txt_instructions_title.pos, 0, 150, 30)
        self.txt_instructions_2 = Text("F J for red notes", self.txt_instructions_title.pos, 0, 170, 30)
        self.txt_instructions_3 = Text("Play with wired headphones for lowest audio latency", 
                                       self.txt_instructions_title.pos, 0, 200, 30)
        self.txt_instructions_exit = Text("Return", self.txt_instructions_title.pos, 0, 240, 30, font_col=COL_YELLOW)
        self.gui_blue_note_pos = (self.txt_instructions_1.pos[0] + 200, self.txt_instructions_1.pos[1] + 10)
        self.gui_red_note_pos = (self.txt_instructions_2.pos[0] + 200, self.txt_instructions_2.pos[1] + 10)


        
        #endregion

        # Flags
        self.quit_game_flag = False # Tells Main to quit the game
        self.song_selected_flag = False # Tells Main that a song has been selected

#region SCREEN_TitleScreen
    def screen_start_screen(self, screen, event):
        self.txt_title.draw(screen)

        self.txt_title_start.set_col(self.get_color(0)) 
        self.txt_title_start.draw(screen)
        self.txt_title_instructions.set_col(self.get_color(1))
        self.txt_title_instructions.draw(screen)
        self.txt_title_exit.set_col(self.get_color(2))
        self.txt_title_exit.draw(screen)

        for event in event:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.title_menu_item = loop(self.title_menu_item - 1, 0, self.title_menu_item_max)
                if event.key == pygame.K_DOWN:
                    self.title_menu_item = loop(self.title_menu_item + 1, 0, self.title_menu_item_max)
                if event.key == pygame.K_RETURN:
                    match self.title_menu_item:
                        case 0: self.page_num = 1
                        case 1: self.page_num = 2
                        case 2: self.quit_game_flag = True
                if event.key == pygame.K_ESCAPE:
                    self.quit_game_flag = True

    def get_color(self, index):
        if index == self.title_menu_item:
            return COL_YELLOW
        else:
            return COL_WHITE

#endregion

#region SCREEN_SongSelect

    def screen_song_select(self, screen, event):
        if self.new_song_selected:            
            pygame.mixer.music.load(self.curr_song_data['wave_path'])
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(loops= 20, start = self.curr_song_data['demostart'], fade_ms= 200)
            self.new_song_selected = False

            self.txt_song_title.set_text(self.curr_song_data['name'])
            self.txt_song_subtitle.set_text(self.curr_song_data['subtitle'])
            self.txt_song_artist.set_text(self.curr_song_data['artist'])
            self.txt_score.set_text(f"HI SCORE {self.hi_scores_arr[self.curr_song_index]}")
             
        # Display current song info
        self.txt_song_title.draw(screen)
        self.txt_song_subtitle.draw(screen)
        self.txt_song_artist.draw(screen)
        self.txt_score.draw(screen)

        song_num = f"{self.curr_song_index + 1} / {len(self.songs_arr)}"
        text = self.font.render(song_num, True, COL_WHITE)
        screen.blit(text, (self.rect_song.centerx - text.size[0] * 0.5, self.rect_song.bottom + 25))

        # Display Other GUI
        pygame.draw.rect(screen, COL_WHITE, self.rect_song, 2)
        pygame.draw.polygon(screen, COL_WHITE, self.gui_tri_up_points, 0)
        pygame.draw.polygon(screen, COL_WHITE, self.gui_tri_bottom_points, 0)

        for event in event:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.curr_song_index = loop(self.curr_song_index - 1, 0, len(self.songs_arr) - 1)
                    self.curr_song_data = self.songs_arr[self.curr_song_index]
                    self.new_song_selected = True
                if event.key == pygame.K_DOWN:
                    self.curr_song_index = loop(self.curr_song_index + 1, 0, len(self.songs_arr) - 1)
                    self.curr_song_data = self.songs_arr[self.curr_song_index]
                    self.new_song_selected = True
                if event.key == pygame.K_RETURN:
                    self.start_game()
                if event.key == pygame.K_ESCAPE:
                    self.page_num = 0

    # Set up songs for the song selection screen
    def init_songs(self, dir):
        # Get Song Data, i.e. song title
        for foldername, subfolders, filenames in walk(dir):
            # print(foldername)
            for filename in filenames:
                # print(filename)
                if filename.endswith('.json'):
                    try:
                        with open(f"{foldername}/{filename}", 'r') as f:
                            data = json.load(f)
                        wave_path = foldername + "/" + data['wave']
                        chart_path = foldername + "/" + filename
                        score_path = foldername + "/" + "score.json"
                        song_name = data['title']
                        song_subtitle = data['subtitle']
                        song_artist = data['artist']
                        song_demostart = data['demostart']
                        self.songs_arr.append({'wave_path': wave_path, 'chart_path': chart_path,
                                               'score_path': score_path, 
                                              'name': song_name, 'subtitle': song_subtitle, 
                                              'artist': song_artist, 'demostart': song_demostart})
                    except Exception as ex:
                        print("ERR in init_songs")
                        print(ex)
        if len(self.songs_arr) > 0:
            self.curr_song_index = 0
            self.curr_song_data = self.songs_arr[0]

        # Get Hi Score Data
        for song in self.songs_arr:
            hi_score = 0
            try:
                with open(song['score_path'], 'r') as f:
                    data = json.load(f)
                    hi_score = data['hi_score']
            except FileNotFoundError:
                pass
            self.hi_scores_arr.append(hi_score)
            
    def start_game(self):
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        self.song_selected_flag = True

    def get_chart(self):
        return self.curr_song_data['chart_path']

#endregion

#region SCREEN_Instructions
    def screen_instructions(self, screen, event):
        self.txt_instructions_title.draw(screen)
        self.txt_instructions_1.draw(screen)
        self.txt_instructions_2.draw(screen)
        self.txt_instructions_3.draw(screen)

        self.txt_instructions_exit.draw(screen)

        pygame.draw.circle(screen, COL_NOTE_BLUE, self.gui_blue_note_pos, NOTE_RADIUS)
        pygame.draw.circle(screen, COL_NOTE_RED, self.gui_red_note_pos, NOTE_RADIUS)

        for event in event:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.page_num = 0
                if event.key == pygame.K_ESCAPE:
                    self.page_num = 0

#endregion

    def update(self, screen, event):
        if self.page_num == 0:
            self.screen_start_screen(screen, event)
        elif self.page_num == 1:
            self.screen_song_select(screen, event)
        elif self.page_num == 2:
            self.screen_instructions(screen, event)

    # Switching Game States
    def switching_from(self):
        self.song_selected_flag = False
        self.new_song_selected = False

    def switching_to(self):
        self.new_song_selected = True
        


