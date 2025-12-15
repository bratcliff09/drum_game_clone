import pygame
from constants import SCREEN_SIZE
from Utils.page_elements import Text

class ScoreScreen:
    def __init__(self):
        self.txt_results = Text("RESULTS", (0, 0), 20, 20, 52)
        self.txt_name = Text("Toamre!!", (0, 0), 60, 60, 30)
        buffer = 60 + 120
        self.txt_good = Text("GOOD 0", (0, 0), 60, buffer, 30)
        self.txt_miss = Text("MISS 0", (0, 0), 60, buffer + 25, 30)
        self.txt_max_combo = Text("MAX COMBO 0", (0, 0), 60, buffer + 50, 30)
        buffer += 50 + 50
        self.txt_clear_score = Text("Clear Score 000000", (0, 0), 60, buffer, 30)
        self.txt_score = Text("SCORE 000000", (0, 0), 60, buffer + 25, 52)
        self.txt_new_score = Text("NEW HI SCORE!!", (0, 0), 100, buffer + 75, 30)

        self.txt_continue = Text("Press any button to continue...", SCREEN_SIZE, -350, -30, 30, None)
        self.txt_determinant = Text("PASSED", (SCREEN_SIZE[0] * 0.5, SCREEN_SIZE[1] * 0.5), 80, -40, 108)

        self.is_new_hi_score = False

        self.flag_leave_score_screen = False


    def update(self, screen: pygame.Surface):
        self.txt_results.draw(screen)
        self.txt_name.draw(screen)
        self.txt_good.draw(screen)
        self.txt_miss.draw(screen)
        self.txt_max_combo.draw(screen)
        self.txt_clear_score.draw(screen)

        self.txt_determinant.draw(screen)

        self.txt_score.draw(screen)

        self.txt_continue.draw(screen)

        if self.is_new_hi_score:
            self.txt_new_score.draw(screen)

    # Centers the rect on screen
    def create_center_rect(self, width, height):
        left = (SCREEN_SIZE[0] * 0.5) - (width * 0.5)
        top = (SCREEN_SIZE[1] * 0.5) - (height * 0.5)
        return pygame.Rect(left, top, width, height)
    
    # Set GOOD, MISS, Score, etc.
    def set_values(self, title, good_count, miss_count, max_combo, 
                   score, clear_score, hi_score):
        self.txt_name.set_text(title)
        self.txt_good.set_text(f"GOOD {good_count}")
        self.txt_miss.set_text(f"MISS {miss_count}")
        self.txt_max_combo.set_text(f"MAX COMBO {max_combo}")
        self.txt_clear_score.set_text(f"Clear Score {clear_score}")
        self.txt_score.set_text(f"SCORE {score}")

        if score >= clear_score:
            passed = "PASSED!!"
        else:
            passed = "FAILURE"
        self.txt_determinant.set_text(passed)

        self.is_new_hi_score = score > hi_score

    def on_key_pressed(self, input):
        self.flag_leave_score_screen = True

    