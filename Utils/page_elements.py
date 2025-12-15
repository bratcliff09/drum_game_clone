from pygame import Font, Surface
from constants import COL_WHITE

# Specifically for placing Text relative to specific points in screen space
class Text:
    def __init__(self, text: str, ref_point, x: float, y: float, 
                 font_size: int, font_type = None, font_col = COL_WHITE):
        self.font = Font(font_type, size=font_size)
        
        self.text_str = text
        self.col = font_col
        self.txt = self.font.render(text, True, font_col)
        
        self.ref_point = ref_point
        self.x = x
        self.y = y
        self.pos = (ref_point[0] + x, ref_point[1] + y)
        
    '''
    # Called after the txt or pos is changed
    def reset(self):
        self.txt = self.font.render(self.text_str, True, self.col)
        self.pos = (self.ref_point[0] + self.x, self.ref_point[1] + self.y)
    '''
        
    def set_text(self, str):
        self.text_str = str
        self.txt = self.font.render(self.text_str, True, self.col)
    
    def set_pos(self, x, y):
        self.x = x
        self.y = y
        self.pos = (self.ref_point[0] + self.x, self.ref_point[1] + self.y)

    def set_col(self, col):
        self.col = col
        self.txt = self.font.render(self.text_str, True, self.col)

    def draw(self, screen: Surface):
        screen.blit(self.txt, self.pos)