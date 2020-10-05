
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
import random
import sys
from collections import deque

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

# initialize simpy
env = simpy.Environment()

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

#SIM
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
NEW_OPPS = 5  # Total number of opportunities
INTERVAL_OPPS = 10.0  # Generate new opportunities roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience




#     ____  ____       _ ______ _____ _______ _____
#    / __ \|  _ \     | |  ____/ ____|__   __/ ____|
#   | |  | | |_) |    | | |__ | |       | | | (___
#   | |  | |  _ < _   | |  __|| |       | |  \___ \
#   | |__| | |_) | |__| | |___| |____   | |  ____) |
#    \____/|____/ \____/|______\_____|  |_| |_____/
#
#

class SIMObserver:
    def __init__(self):
        self.sim_queue = deque()

    def add_sim_event(self, sim_event):
        self.sim_queue.append(sim_event)
        print(self.sim_queue)


#     _____ _____ __  __
#    / ____|_   _|  \/  |
#   | (___   | | | \  / |
#    \___ \  | | | |\/| |
#    ____) |_| |_| |  | |
#   |_____/|_____|_|  |_|
#

class Source:
    def __init__(self, env):
        self.env = env
        self.service_div = simpy.Resource(self.env, capacity=1)

        self.env.process(self.source(env, NEW_OPPS, INTERVAL_OPPS, self.service_div))
        event_log = (self.env.now, "SOURCE_A", "SOURCE")
        record.add_sim_event(event_log)

    def source(self, env, number, interval, service_div):
        """Source generates opportunities randomly"""
        for i in range(number):
            opp = Opportunity(env, f'Opp{i}', service_div, time_in_queue=12.0)
            t = random.expovariate(1.0 / interval)
            yield env.timeout(t)

class Opportunity:
    def __init__(self, env, name, service_div, time_in_queue):
        self.env = env
        self.name = name
        self.service_div = service_div
        self.time_in_queue = time_in_queue

        self.env.process(self.create_opp(self.env, self.name, self.service_div, self.time_in_queue))

    def create_opp(self, env, name, service_div, time_in_queue):
        """Opportunity arrives, is served or abandon."""
        arrive = env.now
        print(f'{arrive:.2f} {name}: NEW OPP')
        event_log = (self.env.now, name, "OPP")
        record.add_sim_event(event_log)

        with service_div.request() as req:
            patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
            # Wait for the Service team or abort at the end of our tether
            results = yield req | env.timeout(patience)

            wait = env.now - arrive

            if req in results:
                # We got to the project
                print(f'{env.now:.2f} {name}: Waiting {wait:.2f}')

                tib = random.expovariate(1.0 / time_in_queue)
                yield env.timeout(tib)
                print(f'{env.now:.2f} {name}: Finished')

            else:
                # We reneged
                print(f'{env.now:.2f} {name}: RENEGED after {wait:.2f}')


#
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


class OppEntity(pygame.sprite.Sprite):
    def __init__(self, opp_info):
        super(OppEntity, self).__init__()
        self.opp_info = opp_info
        self.opp_time = opp_info[0]
        self.opp_name = opp_info[1]
        self.opp_type = opp_info[2]

        self.surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(center=(200, 200))
        self.light_green = (000, 200, 100, 255)
        pygame.draw.polygon(self.surf, self.light_green, [(12, 0), (36, 0), (50, 25), (36, 50), (12, 50), (0, 25)])

    def update(self, *args):
        self.rect.y += 5


class SourceEntity(pygame.sprite.Sprite):
    def __init__(self, source_info):
        super(SourceEntity, self).__init__()
        self.source_info = source_info
        self.source_time = source_info[0]
        self.source_name = source_info[1]
        self.source_type = source_info[2]

        self.surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(center=(200, 200))
        light_grey = (200, 200, 200)
        pygame.draw.polygon(self.surf, light_grey, [(0, 0), (100, 0), (50, 100)])


class SIMScene(Scene):
    def __init__(self):
        super().__init__()
        print("VIZ Scene")
        self.SOURCE_A_SURF = None
        self.SOURCE_A_RECT = None
        self.OPP_LIST = []
        self.OPP_RECT_LIST = []
        self.LOST_GROUP = pygame.sprite.Group()
        self.PLACED_GROUP = pygame.sprite.Group()

    def sim_create_source(self, create_source_event):
        if create_source_event[1] == "SOURCE_A":
            new_source = SourceEntity(create_source_event)
            self.PLACED_GROUP.add(new_source)

    def process_sim_event(self):
        next_sim_event = record.sim_queue.popleft()
        if next_sim_event[2] == "SOURCE":
            print("FOUND A SOURCE CREATION EVENT")
            self.sim_create_source(next_sim_event)
        if next_sim_event[2] == "OPP":
            print("FOUND AN OPP CREATION EVENT")
            new_opp = OppEntity(next_sim_event)
            self.OPP_LIST.append(new_opp)
            self.OPP_RECT_LIST.append(new_opp.rect)
            self.LOST_GROUP.add(new_opp)

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                print("KEY PRESSED")
                if event.key == pygame.K_SPACE:
                    print("SPACE KEY PRESSED")
                    self.next_scene = None

        queue_peek = len(record.sim_queue) > 0
        while queue_peek:
            if (record.sim_queue[0][0] * 100) <= pygame.time.get_ticks():
                print(f'SIM TICKS: {record.sim_queue[0][0] * 100:.2f}')
                self.process_sim_event()
                print(f'PYGAME TICKS: {pygame.time.get_ticks()}')
                queue_peek = len(record.sim_queue) > 0
            else:
                queue_peek = False

    def update(self):
        for opp_sprite in self.LOST_GROUP.sprites():
            if pygame.sprite.spritecollideany(opp_sprite, self.PLACED_GROUP):
                opp_sprite.update()
            else:
                print("GOT HERE!")
                self.LOST_GROUP.remove(opp_sprite)
                self.PLACED_GROUP.add(opp_sprite)


    def render(self):
        # Set background color
        SCREEN.fill(BLACK)
        # Render Text
        text = pygame.font.Font(None, 64).render("SIM ALPHA", 1, WHITE)
        rect = text.get_rect()
        rect.centerx = SCREEN_WIDTH // 2
        rect.bottom = SCREEN_HEIGHT // 2
        SCREEN.blit(text, rect)
        # Render SIM Objects
        for entity in self.PLACED_GROUP:
            SCREEN.blit(entity.surf, entity.rect)
        for entity in self.LOST_GROUP:
            SCREEN.blit(entity.surf, entity.rect)

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
    print('START VIZ SIM ALPHA....................')

    # RUN SIMULATION FIRST
    record = SIMObserver()
    opportunities = Source(env)
    print('SIM START')
    env.run()
    print('SIM OVER')

    # RUN SIM VIZ
    print('VIZ START')
    first_scene = SIMScene()
    game_dir = Director(first_scene)
    game_dir.action()
    print('VIZ OVER')
    pygame.quit()
    print('END SIM ALPHA.........................')
    sys.exit()


