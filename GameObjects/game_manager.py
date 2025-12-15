import pygame
import json
import os.path

from .input_manager import InputManager
from .composer import Composer
from .conductor import Conductor
from .judge import Judge

from .track import Track
from .note import Note
from .note_vfx import NoteVFX

import constants

from enum import Enum
from CustomEnums.note_hit import NoteHit
from CustomEnums.input_type import InputType

from Utils.timers import Timer
from Utils.page_elements import Text

from GameObjects.score_menu import ScoreScreen


class GameState(Enum):
    LOADING = 1
    PLAYING = 2
    END = 3
    SCORE_SCREEN = 4

class GameManager:
    def __init__(self, chart_json):
        self.input_offset = 0

        # Initalize from chart data and hi-score JSON
        self.song_title : str
        self.bpm : float
        self.chart_dir = os.path.dirname(chart_json)
        self.song_path : str
        self.song_offset : float
        self.song_offset_ms : float
        self.score_multiplier : float
        self.clear_range : float
        self.hi_score_path = f"{self.chart_dir}/score.json"
        self.hi_score : int
        self.measure_data : list[dict]
        self.init_chart_data(chart_json, self.chart_dir)

        # Others
        self.end_beat = -1 # The beat that the song will end on
        self.end_timer = Timer(5) # When the song ends, wait x seconds before going to the Score Screen
        
        self.note_division = self.get_note_division()
        print(f"Notes Divided: {self.note_division}")
        self.notes = self.generate_notes()
        self.active_notes = []
        self.spawn_index = 0

        self.o_Conductor = Conductor(self.bpm, self.song_offset_ms, self.input_offset, self.note_division)
        self.o_Composer = Composer(self.measure_data, self.note_division)

        # The Judge
        self.max_score = len(self.o_Composer.queue) * self.score_multiplier
        self.o_Judge = Judge(self.score_multiplier, self.clear_range, self.max_score, 
                             self.o_Composer.get_next_note, self.o_Conductor.get_active_beat)
        self.o_Conductor.ev_active_beat_exit.observe(self.o_Judge.active_beat_closed)
        self.o_Judge.init_curr_goal(self.o_Composer.get_curr_note())
        self.o_Judge.ev_on_goal_update.observe(self.on_goal_update)

        self.o_InputManager = InputManager()
        self.o_InputManager.ev_key_pressed.observe(self.o_Judge.on_input_pressed)

        #GUI
        self.o_Track = Track(0, 200)
        self.gui_score = pygame.Surface((constants.SCREEN_SIZE[0], 50))
        self.note_vfx = NoteVFX(self.o_Track.gameworld_hit_marker_pos)
        
        self.default_music_vol = 0.1
        self.isMusicPlaying = False
        
        # Text
        self.font = pygame.font.Font(None, size=30) #Uses the default font at size 30px probably
        self.font_center = pygame.font.Font(None, size=30)
        self.font_center.align = pygame.FONT_CENTER

        self.txt_song_fin = Text("Finished", 
                                 (constants.SCREEN_SIZE[0] * 0.5, constants.SCREEN_SIZE[1] * 0.5),
                                   0, -35, 52)
        self.txt_song_title = Text(self.song_title, (constants.SCREEN_SIZE[0], 0), 0, 0, 52)
        self.txt_song_title.set_pos(-self.txt_song_title.txt.width - 20, self.txt_song_title.txt.height - 20)

        # Score Screen
        self.o_ScoreScreen = ScoreScreen()

        self.curr_state = GameState.LOADING
        self.debug = False

        self.is_hi_score_saved = False

    def update_END(self, screen, delta_time):
        # GUI
        self.o_Track.draw_track(screen)        
        txt_combo = self.font_center.render(f"COMBO\n{self.o_Judge.curr_combo}", True, (255,255,255))
        screen.blit(txt_combo, (35, 220))
        
        gui_score_x = 150
        gui_score_y = 300
        screen.blit(self.gui_score, (gui_score_x, gui_score_y))
        txt_missed_note = self.font.render(
            f"GOOD {self.o_Judge.good}     MISSED {self.o_Judge.missed}", True, (255,255,255))
        missed_txt_pos = (gui_score_x + 50, gui_score_y + 20)
        screen.blit(txt_missed_note, missed_txt_pos)

        self.txt_song_fin.draw(screen)

        # Get the remaining notes offscreen
        music_pos = pygame.mixer.music.get_pos()
        for note in self.active_notes:
            note.update_position(music_pos, self.o_Track.gameworld_hit_marker_pos[0])
            note.draw(screen, self.o_Track.gameworld_hit_marker_pos[1])
        self.despawn_notes()

        # Update Timer
        if not self.end_timer.is_active():
            self.curr_state = GameState.SCORE_SCREEN
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
        else:
            self.end_timer.tick(delta_time)
            # Manually fading out song because music.fadeout blocks event calls
            vol = self.end_timer.timer / self.end_timer.timer_max * self.default_music_vol
            pygame.mixer.music.set_volume(vol)
    
    def update(self, screen, event, delta_time):
        match (self.curr_state):
            case GameState.LOADING: self.update_LOADING()
            case GameState.PLAYING: self.update_PLAYING(screen, event, delta_time)
            case GameState.END: self.update_END(screen, delta_time)
            case GameState.SCORE_SCREEN: self.update_SCORE_SCREEN(screen, event)
    
    #region GAMESTATE SCORE_SCREEN
    def update_SCORE_SCREEN(self, screen, event):
        self.o_ScoreScreen.update(screen)

        self.o_InputManager.update(event)

        if not self.is_hi_score_saved:
            self.save_hi_score()
            self.is_hi_score_saved = True

        for event in event:
          if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                   self.o_ScoreScreen.flag_leave_score_screen = True
                
    
    # Save HI Score to same dir as the chart
    def save_hi_score(self):
        # Deterimine if current score > hi score
        curr_score = self.o_Judge.get_score()
        if curr_score <= self.hi_score: return

        # Save if so
        try:
            with open(self.hi_score_path, 'w') as f:
                data = {'hi_score': curr_score}
                json.dump(data, f)
        except Exception as ex:
            print(ex)

    #endregion

    #region GameState LOADING
    def update_LOADING(self):
        pygame.mixer.music.load(self.song_path)
        pygame.mixer.music.set_volume(self.default_music_vol)
        self.curr_state = GameState.PLAYING

    # Get the note division of the song based on the first row
    #   Eight notes, 16th notes, 12th notes?
    def get_note_division (self):
         for measure in self.measure_data:
            row = measure['notes']
            # print("ROW LENGTH: " + str(len(row)))
              
            if row.strip() == "": continue # Ignore empty rows
            note_division = len(row) / 4
            if not note_division.is_integer():
                print("WARNING: Note Division is not a whole number")
                print("Defaulting to quarter notes") 
                note_division = 1
            return note_division
    
    def generate_notes(self):           
            # Defaults
            time_sig = (4, 4) # 4/4
            scroll_spd = 1

            # Get the subNote duration. An eight note lasts for 500ms at BPM 60
            subnote_duration = 60 / (self.bpm * self.note_division) * 1000
            elotted_duration = self.song_offset_ms
            curr_beat = 1 # What beat the note lies on

            spd = constants.BASE_SPD
            time_it_will_take = constants.SPAWN_POINT / spd
            #   Time it will take the note to travel from spawn to the hit marker

            arr = []
            for measure in self.measure_data:
                if "end" in measure:
                    self.end_beat = curr_beat
                    break

                if "time_sig" in measure:
                    time_sig = measure['time_sig'].split('/')
                    time_sig = (int(time_sig[0]), int(time_sig[1])) 

                if 'scroll_spd' in measure:
                    scroll_spd = measure['scroll_spd']
                    spd = constants.BASE_SPD * scroll_spd
                    time_it_will_take = constants.SPAWN_POINT / spd
                
                row = measure["notes"]
                if row.strip() == "": 
                    elotted_duration += (subnote_duration * time_sig[0] * self.note_division)
                    curr_beat += (self.note_division * time_sig[0])
                    continue

                row = list(row)
                for n in row:
                    if n != '0':
                        note_type = InputType.DON
                        if n == '2':
                            note_type = InputType.KAT

                        spawn_time = elotted_duration - time_it_will_take
                        arr.append(Note(note_type, elotted_duration, spawn_time, curr_beat))             
                    elotted_duration += subnote_duration
                    curr_beat += 1
            
            # If the song chart doesn't have an explicit 'end'
            if self.end_beat == -1:
                self.end_beat = curr_beat

            return arr
    
    # Initialize the chart data (bpm, song title, etc)
    def init_chart_data(self, chart_json, chart_dir):
        # Get chart data
        with open (chart_json, 'r') as f:
            data = json.load(f)
        
        self.song_title = data['title']
        self.bpm = data['bpm']
        self.song_path = f"{chart_dir}/{data['wave']}"
        self.song_offset = data['offset'] * -1
        self.song_offset_ms = self.song_offset * 1000
        self.measure_data = data['measures']
        
        # if score multiplier or clear range missing
        if 'score_multiplier' in data:
            self.score_multiplier = data['score_multiplier']
        else:
            self.score_multiplier = 1
            print("ERR: Score Multiplier not set in chart")
        
        if 'clear_range' in data:
            self.clear_range = data['clear_range']
        else:
            self.clear_range = 0.2
            print("ERR: Clear Range not set in chart")

        # Get the hi score JSON via chart_directory
        try:
            with open(self.hi_score_path, 'r') as f:
                data = json.load(f)
            self.hi_score = data['hi_score']
        except FileNotFoundError:
            print("ERR: HI Score file doesn't exist")
            self.hi_score = 0
            # A hi_score file will be created at the end of the song        
    
    #endregion

    #region GameState PLAYING
    def update_PLAYING(self, screen, event, delta_time):
        if not self.isMusicPlaying:
            pygame.mixer.music.play(1)
            self.isMusicPlaying = True

        # Display GUI 1
        self.o_Track.draw_track(screen)
        self.txt_song_title.draw(screen)
        screen.blit(self.gui_score, (150, 300))

        #Display the music time position
        musicPos = pygame.mixer.music.get_pos()
        if self.debug:
            text = self.font.render(str(musicPos), True, (0,0,0)) # In MS
            screen.blit(text, (300, 50))
            text1 = self.font.render("{:.3f}".format(musicPos * .001), True, (0,0,0)) # In Seconds
            screen.blit(text1, (300, 70))
        
        # Updates the conductor
        self.o_Conductor.update_no_offset(musicPos)
        self.o_Conductor.update_offset(musicPos)
        if self.debug:
            beatPosText = self.font.render(f"Beat: {self.o_Conductor.get_current_beat()}", True, (0,0,0))
            screen.blit(beatPosText, (300, 90))

        # Check if it's the end of the song
        if self.o_Conductor.curr_beat >= self.end_beat:
            self.switch_to_GameState_END()

        # Update Input Manager
        self.o_InputManager.update(event)
        if self.debug:
            self.o_InputManager.debugDraw(True, (20, 20), screen)
        
        # Draw / Spawn / Despawn Notes      
        self.spawn_notes(musicPos)
        for note in self.active_notes:
            note.update_position(musicPos, self.o_Track.gameworld_hit_marker_pos[0])
            note.draw(screen, self.o_Track.gameworld_hit_marker_pos[1])
        self.despawn_notes() 

        # Draw Note Hit / Miss VFX
        self.note_vfx.update(screen, delta_time)

        # GUI 2
        # Visual Input Feedback
        self.o_Track.draw_input_drums(screen, self.o_InputManager.get_held_inputs())
        # Draw Score / Hit and Missed Notes
        txt_missed_note = self.font.render(
            f"GOOD {self.o_Judge.good}     MISSED {self.o_Judge.missed}", True, (255,255,255))
        missed_txt_pos = (150 + 50, 300 + 20)
        screen.blit(txt_missed_note, missed_txt_pos)
        # Draw Combo
        txt_combo = self.font_center.render(f"COMBO\n{self.o_Judge.curr_combo}", True, (255,255,255))
        screen.blit(txt_combo, (35, 220))

        # Exit gameplay and return to Main Menu
        for event in event:
          if event.type == pygame.KEYDOWN:
               if event.key == pygame.K_ESCAPE:
                   self.o_ScoreScreen.flag_leave_score_screen = True


    def spawn_notes(self, music_pos):        
            for i in range(self.spawn_index, len(self.notes)):
                note = self.notes[i]
                if note.spawn_time > music_pos: break
                
                self.active_notes.append(note)
                self.spawn_index += 1

    def despawn_notes(self):
        counter = -1
        for notes in self.active_notes:
            # Find the first note.kill that isn't False
            if not notes.kill: break
            counter += 1
        if counter >= 0:
            # print(f"LOG: notes[0:{counter+1}]")
            del self.active_notes[0:counter+1]
    
    # Changes the note status based on The Judge
    #   A Judge Event triggered when a note is missed or good
    def on_goal_update(self, goal):
        if goal['status'] == NoteHit.MISS:
            self.note_vfx.animation_active(NoteHit.MISS)
            for note in self.active_notes:
                if note.beat == goal['beat']:
                    note.color = (0, 0, 0)
                    break
                if note.beat > goal['beat']: 
                    break
        elif goal['status'] == NoteHit.GOOD:
            self.note_vfx.animation_active(NoteHit.GOOD)

    def switch_to_GameState_END(self):
        # Swap to Gamestate END
        self.curr_state = GameState.END
        
        # Get values needed for the score screen
        good_count = self.o_Judge.good
        missed_count = self.o_Judge.missed
        max_combo = self.o_Judge.max_combo
        score = self.o_Judge.get_score()
        clear_score = self.o_Judge.clear_score
        
        self.o_ScoreScreen.set_values(
            self.song_title, good_count, missed_count, max_combo, 
            score, clear_score, self.hi_score)
        
        # Give Score Screen the input event
        self.o_InputManager.ev_key_pressed.observe(self.o_ScoreScreen.on_key_pressed)

    #endregion