
#    _____                            _
#   |_   _|                          | |
#     | |  _ __ ___  _ __   ___  _ __| |_ ___
#     | | | '_ ` _ \| '_ \ / _ \| '__| __/ __|
#    _| |_| | | | | | |_) | (_) | |  | |_\__ \
#   |_____|_| |_| |_| .__/ \___/|_|   \__|___/
#                   | |
#                   |_|

import pygame
import simpy

#     _____      _
#    / ____|    | |
#   | (___   ___| |_ _   _ _ __
#    \___ \ / _ \ __| | | | '_ \
#    ____) |  __/ |_| |_| | |_) |
#   |_____/ \___|\__|\__,_| .__/
#                         | |
#                         |_|

# initialize pygame
pygame.init()

# Timer
clock = pygame.time.Clock()

#     _____                _              _
#    / ____|              | |            | |
#   | |     ___  _ __  ___| |_ __ _ _ __ | |_ ___
#   | |    / _ \| '_ \/ __| __/ _` | '_ \| __/ __|
#   | |___| (_) | | | \__ \ || (_| | | | | |_\__ \
#    \_____\___/|_| |_|___/\__\__,_|_| |_|\__|___/
#
#

# Window
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
TITLE = "Simulation: TEST"

# Initialize the game screen
SCREEN = pygame.display.set_mode(SIZE)
pygame.display.set_caption(TITLE)

# Clock frame rate
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
CHOCOLATE = (210, 105, 30)

#    _____  _               _
#   |  __ \(_)             | |
#   | |  | |_ _ __ ___  ___| |_ ___  _ __
#   | |  | | | '__/ _ \/ __| __/ _ \| '__|
#   | |__| | | | |  __/ (__| || (_) | |
#   |_____/|_|_|  \___|\___|\__\___/|_|
#
#
class Director:
    def __init__(self, start_scene):
        self.active_scene = start_scene

    def is_quit_event(self, event, pressed_keys):
        x_out = event.type == pygame.QUIT
        ctrl = pressed_keys[pygame.K_LCTRL] or pressed_keys[pygame.K_RCTRL]
        q = pressed_keys[pygame.K_q]

        return x_out or (ctrl and q)

    def action(self):
        while self.active_scene is not None:
            # event handling
            pressed_keys = pygame.key.get_pressed()
            filtered_events = []

            for event in pygame.event.get():
                if self.is_quit_event(event, pressed_keys):
                    self.active_scene.terminate()
                else:
                    filtered_events.append(event)

            # game logic
            self.active_scene.process_input(filtered_events, pressed_keys)
            self.active_scene.update()
            self.active_scene.render()
            self.active_scene = self.active_scene.next_scene

            # update and tick
            pygame.display.flip()
            clock.tick(FPS)


#     _____
#    / ____|
#   | (___   ___ ___ _ __   ___  ___
#    \___ \ / __/ _ \ '_ \ / _ \/ __|
#    ____) | (_|  __/ | | |  __/\__ \
#   |_____/ \___\___|_| |_|\___||___/
#
#

class Scene:
    def __init__(self):
        self.next_scene = self

    def process_input(self, events, pressed_keys):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def render(self):
        raise NotImplementedError

    def terminate(self):
        self.next_scene = None


class SIMScene(Scene):
    def __init__(self):
        super().__init__()
        print("SIM Scene")

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                print("KEY PRESSED")
                if event.key == pygame.K_SPACE:
                    print("SPACE KEY PRESSED")
                    self.next_scene = None

    def update(self):
        pass

    def render(self):
        SCREEN.fill(BLACK)
        text = pygame.font.Font(None, 64).render("SIM FIELD", 1, WHITE)
        rect = text.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.bottom = SCREEN_HEIGHT // 2
        SCREEN.blit(text, rect)

    def terminate(self):
        self.next_scene = None


#    __  __       _
#   |  \/  |     (_)
#   | \  / | __ _ _ _ __
#   | |\/| |/ _` | | '_ \
#   | |  | | (_| | | | | |
#   |_|  |_|\__,_|_|_| |_|
#
#
# START THE SIM
if __name__ == "__main__":
    # Setup and start the simulation
    print('VIZ SIM ALPHA')
    env = simpy.Environment()
    first_scene = SIMScene()
    game_dir = Director(first_scene)
    game_dir.action()
    pygame.quit()
    print('END SIM.........................')


