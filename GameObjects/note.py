import pygame
from constants import COL_NOTE_RED, COL_NOTE_BLUE, SPAWN_POINT, NOTE_RADIUS
from CustomEnums.input_type import InputType

class Note:   
    def __init__(self, note_type: InputType, time_needed: float, spawn_time: float, beat: int):
        self.color = COL_NOTE_RED
        if note_type == InputType.KAT:
            self.color = COL_NOTE_BLUE
        
        self.beat = beat # On what beat does the note lie

        self.time_needed = time_needed # Time the note occurs in song
        self.spawn_time = spawn_time # Time this note should be spawned

        self.slope = (0 - SPAWN_POINT) / (time_needed - spawn_time)

        self.x = 0

        self.kill = False # Used to despawn the notes
    
    def draw(self, screen, y_pos):
        pygame.draw.circle(screen, self.color, (self.x, y_pos), NOTE_RADIUS, 0)

    def update_position(self, music_pos, hit_marker_x):
        self.x = (music_pos - self.time_needed) * self.slope
        self.x = hit_marker_x + self.x

        if self.x < -NOTE_RADIUS: self.kill = True