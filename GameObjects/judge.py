import pygame
from Utils.event import Event
from CustomEnums.input_type import InputType
from CustomEnums.note_hit import NoteHit
from math import floor, ceil

# Determines score and if the player hit the note at the right time
class Judge:
    def __init__(self, score_multiplier, clear_range, max_score, cb_composer_get_goal, 
                 cb_conductor_get_active_beat):
        # Score
        self.good = 0
        self.missed = 0

        self.clear_score = floor(max_score * clear_range)
        self.score_multiplier = score_multiplier

        self.curr_combo = 0
        self.max_combo = 0
        
        self.curr_goal = -1
        self.curr_goal_beat = -1
        self.curr_goal_input = -1

        self.cb_get_next_goal = cb_composer_get_goal
        self.cb_get_active_beat = cb_conductor_get_active_beat

        self.ev_on_goal_update = Event()

    # Tells the Judge that the active beat window has passed
    #   Signaled by the Conductor
    def active_beat_closed(self, then_active_beat):
        # print(f"Then: {then_active_beat} | Goal: {self.curr_goal_beat}")
        if then_active_beat == self.curr_goal_beat:
            self.missed += 1
            self.reset_combo()
            self.ev_on_goal_update.notify_args({
                'beat': self.curr_goal_beat,
                'status': NoteHit.MISS
            })
            self.update_curr_goal()

    def update_curr_goal(self):
        # Get the beat and what input they're suppose to play
        new_goal = self.cb_get_next_goal()
        if new_goal['beat'] == -1:
            self.curr_goal_beat = -1
            self.curr_goal_input = -1
        else:
            self.curr_goal_beat = new_goal['beat']
            self.curr_goal_input = new_goal['key']

    # Only called by the game_manager when initializing the Judge
    def init_curr_goal(self, first_goal_beat):
        self.curr_goal_beat = first_goal_beat['beat']
        self.curr_goal_input = first_goal_beat['key']
    
    def increment_combo(self):
        self.curr_combo += 1
        if self.curr_combo > self.max_combo:
            self.max_combo = self.curr_combo
    
    def reset_combo(self):
        self.curr_combo = 0

    def on_input_pressed(self, input):
        # Unless the input matches the goal input, we don't care
        if input != self.curr_goal_input: return

        # Get the current active beat
        active_beat = self.cb_get_active_beat()
        if active_beat != self.curr_goal_beat: return

        self.good += 1
        self.increment_combo()
        self.ev_on_goal_update.notify_args({
            'beat': self.curr_goal_beat,
            'status': NoteHit.GOOD
        })
        self.update_curr_goal()
    
    def get_score(self):
        return ceil(self.good * self.score_multiplier)