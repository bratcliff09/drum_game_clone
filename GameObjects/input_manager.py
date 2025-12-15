import pygame
from Utils.event import Event
from CustomEnums.input_type import InputType

# Records player inputs and broadcasts on key input
class InputManager:
    def __init__(self):
        self.key_D = {'active': False, 'key_enum': pygame.K_d, 'type': InputType.KAT} #Was the D key pressed this frame or being held down?
        self.key_F = {'active': False, 'key_enum': pygame.K_f, 'type': InputType.DON}
        self.key_J = {'active': False, 'key_enum': pygame.K_j, 'type': InputType.DON}
        self.key_K = {'active': False, 'key_enum': pygame.K_k, 'type': InputType.KAT}
        self.ev_key_pressed = Event()
        self.ev_key_released = Event()

        self.font = pygame.font.Font(None, size=30)

    def update(self, event):
        key_arr = [self.key_D, self.key_F, self.key_J, self.key_K]
        for event in event:
            if event.type == pygame.KEYDOWN:
                for key in key_arr:
                    if event.key == key['key_enum']:
                        key['active'] = True
                        self.ev_key_pressed.notify_args(key['type'])
            if event.type == pygame.KEYUP:
                for key in key_arr:
                    if event.key == key['key_enum']:
                        key['active'] = False
                        self.ev_key_released.notify_args(key['type'])

    def get_held_inputs(self):
        is_DON_active = False
        is_KAT_active = False
        
        for key in [self.key_D, self.key_F, self.key_J, self.key_K]:
            if key['active']:
                if key['type'] == InputType.DON:
                    is_DON_active = True
                elif key['type'] == InputType.KAT:
                    is_KAT_active = True
        return {'DON': is_DON_active, 'KAT': is_KAT_active}

    def debugDraw(self, isActive, origin, screen):
        if not isActive: return

        key_arr = [self.key_D, self.key_F, self.key_J, self.key_K]
        i = 0

        for key in key_arr:
            text = self.font.render(f"Key {i}: {str(key['active'])}", True, (0,0,0))
            screen.blit(text, (origin[0], origin[1] + (20 * i)))
            i += 1
