import pygame
import constants
        
class Track:
    def __init__(self, xPos: int, yPos: int):
        self.pos = (xPos, yPos)
        self.width = constants.SCREEN_SIZE[0] - xPos
        self.height = 100
        self.color = (39, 43, 73)

        self.drum_half = 150 # x-position
        self.hit_marker_pos = (self.drum_half + 60, int(self.height * 0.5)) # (x, y)
        self.gameworld_hit_marker_pos = (xPos + self.hit_marker_pos[0], yPos + self.hit_marker_pos[1])

        self.surface = self.gui_track = pygame.Surface(
            (constants.SCREEN_SIZE[0], self.height))
        self.init_surface()

        self.input_pos = (int(xPos + self.drum_half * 0.5), int(yPos + self.height * 0.5))
        self.radius = 35

    
    def init_surface(self):
        # BG
        self.surface.fill(self.color)

        # Draw drum half
        pygame.draw.line(self.surface, (255,255,255),
                         (self.drum_half, 0), (self.drum_half, self.height))
        pygame.draw.circle(self.surface, (255,255,255), 
                           (int(self.drum_half * 0.5), int(self.height * 0.5)),
                           35, 1)
        
        # Draw track
        pygame.draw.circle(self.surface, (255, 255, 255, 0.35), self.hit_marker_pos, 25, 2)

    def draw_track(self, screen: pygame.Surface):
        screen.blit(self.surface, self.pos)
    
    def draw_input_drums(self, screen, inputs):
        if inputs['DON']:
            pygame.draw.circle(screen, constants.COL_NOTE_RED, self.input_pos, self.radius, 0, draw_top_left=True, draw_bottom_left=True)
        if inputs['KAT']:
            pygame.draw.circle(screen, constants.COL_NOTE_BLUE, self.input_pos, self.radius, 0, draw_top_right=True, draw_bottom_right=True)