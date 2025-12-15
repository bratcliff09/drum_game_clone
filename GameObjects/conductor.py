from pygame import mixer
import constants
from Utils.event import Event

# Keeps track of the beat on two tracks: One for visuals and audio, the other offsetted by input delay
class Conductor:
    def __init__(self, bpm, start_offset, input_offset = 0, sub_note = 1 ):
        self.bpm = bpm
        self.sub_beat_duration = 60 / (bpm * sub_note) * 1000
            # If subNotes = 1, it counts every quarter note. If 2, it counts every eighth note

        self.sub_note = sub_note
        self.startOffset = start_offset

        self.prev_beat_pos = -1
        self.next_beat_pos = start_offset
        self.last_beat = 0
        self.curr_beat = 1

        # Input Offset
        self.off_prev_beat_pos = -1
        self.off_next_beat_pos = start_offset - input_offset
        self.off_last_beat = 0
        self.off_curr_beat = 1

        #Error Margin - Only used by Input Offset
        self.margin = constants.HR_GOOD
        self.active_beat = -1
        #   If -1, that means the player is outside of the 'GOOD' hit range of the beat
        #   If != -1, the player is w/i the hit range
        self.active_beat_start_pos = self.off_next_beat_pos - self.margin
        self.active_beat_end_pos = self.off_next_beat_pos + self.margin

        self.metronome_sound = mixer.Sound('./Assets/UIBack.wav')
        self.metronome_on = False

        self.ev_active_beat_exit = Event()

    def update_no_offset(self, music_pos):        
        if music_pos > self.next_beat_pos:
            self.prev_beat_pos = self.next_beat_pos
            self.next_beat_pos += self.sub_beat_duration
            self.last_beat = self.curr_beat
            self.curr_beat += 1
            
            if self.metronome_on:
                if (self.curr_beat - 1) % self.sub_note == 0:
                    self.metronome_sound.play()
    
    def update_offset(self, music_pos):        
        if music_pos >= self.active_beat_end_pos:
                self.ev_active_beat_exit.notify_args(self.active_beat)
                self.active_beat = -1
                self.active_beat_end_pos = self.off_next_beat_pos + self.margin

        if self.active_beat == -1: 
            if music_pos >= self.active_beat_start_pos:
                self.active_beat = self.off_curr_beat

        if music_pos >= self.off_next_beat_pos:
            self.off_prev_beat_pos = self.off_next_beat_pos
            self.off_next_beat_pos += self.sub_beat_duration
            self.off_last_beat = self.off_curr_beat
            self.off_curr_beat += 1
            
            self.active_beat_start_pos = self.off_next_beat_pos - self.margin
        
    def get_current_beat(self):
        return self.curr_beat
    
    def get_active_beat(self):
        return self.active_beat
    
    def get_beat_info(self):
        return {
            'prev_beat_pos': self.off_prev_beat_pos,
            'next_beat_pos': self.off_next_beat_pos,
            'last_beat': self.off_last_beat,
            'curr_beat': self.off_curr_beat
        }
    
    