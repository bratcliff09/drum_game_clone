import pygame
from CustomEnums.note_hit import NoteHit
from constants import COL_YELLOW
from Utils.cool_maths import clamp
from Utils.timers import Timer

class NoteVFX:
    def __init__(self, hit_marker_pos):
        self.pos = hit_marker_pos
        self.radius = 30

        self.anim_active = False
        self.timer = Timer(1.05)
        self.timer_circle = Timer(0.3)
        self.timer_circle.timer = 0

        self.font = pygame.font.Font(None, size = 30)
        self.col_good = COL_YELLOW
        self.col_miss = (56, 151, 224)
        self.txt_pos = (self.pos[0] - 30, self.pos[1] - 45)
        self.txt_good = self.font.render("GOOD", True, self.col_good)
        self.txt_miss = self.font.render("MISS", True, self.col_miss)
        self.curr_txt = self.txt_good


    def update(self, screen: pygame.Surface, delta_time):
        if not self.anim_active: return

        self.timer.tick(delta_time)
        self.timer_circle.tick(delta_time)

        # alpha = self.time_counter * 255
        self.curr_txt.set_alpha(self.timer.get_percentage() * 255)
        screen.blit(self.curr_txt, self.txt_pos)

        if self.timer_circle.is_active():
            pygame.draw.circle(screen, COL_YELLOW, self.pos, self.radius, 1)     

        if not self.timer.is_active(): 
            self.anim_active = False
            # self.time_counter = self.time_counter_max

    def animation_active(self, note_hit_status: NoteHit):
        self.anim_active = True

        if note_hit_status == NoteHit.GOOD:
            self.curr_txt = self.txt_good
            self.timer_circle.reset()
        elif note_hit_status == NoteHit.MISS:
            self.curr_txt = self.txt_miss

        self.timer.reset()
