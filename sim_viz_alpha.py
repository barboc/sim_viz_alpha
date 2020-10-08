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
from collections import deque, namedtuple
import math
import pprint

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
TITLE = "Simulation: ALPHA"

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
LIGHT_GREEN = (000, 200, 100)
LIGHT_BLUE = (000, 000, 200)
LIGHT_GRAY = (200, 200, 200)

#SIM
RANDOM_SEED = 42
random.seed(RANDOM_SEED)
NEW_OPPS = 10  # Total number of opportunities
INTERVAL_OPPS = 10.0  # Generate new opportunities roughly every x seconds
MIN_PATIENCE = 1  # Min. customer patience
MAX_PATIENCE = 3  # Max. customer patience
RES_A_CAPACITY = 1  # Capacity for Resource A
RES_A_TIME = 10  # Time expect to use resource

# VIZ
SIM_SPEED = 200  # Set to 1000 to match milli-sec speed of pygame

#     ____  ____       _ ______ _____ _______ _____
#    / __ \|  _ \     | |  ____/ ____|__   __/ ____|
#   | |  | | |_) |    | | |__ | |       | | | (___
#   | |  | |  _ < _   | |  __|| |       | |  \___ \
#   | |__| | |_) | |__| | |___| |____   | |  ____) |
#    \____/|____/ \____/|______\_____|  |_| |_____/
#
#

# Create named tuple that will record the SIM in the deque
Log_Event = namedtuple('Log_Event', ['time', 'name', 'type', 'action'])


# Class for recording SIM events to the deque for later playback.
class SIMObserver:
    def __init__(self):
        self.sim_queue = deque()

    def add_sim_event(self, sim_event):
        self.sim_queue.append(sim_event)

    def print_deque(self):
        pprint.pprint(self.sim_queue)


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
        self.service_div = simpy.Resource(self.env, capacity=RES_A_CAPACITY)

        # LOG FIRST RESOURCE CREATE***********
        event_log = Log_Event(round(self.env.now, 2), "RESOURCE_A", "RESOURCE", "CREATE")
        record.add_sim_event(event_log)

        # Add first sim process and pass the resource.
        self.env.process(self.source(env, NEW_OPPS, INTERVAL_OPPS, self.service_div))

        # LOG FIRST SOURCE CREATE***********
        event_log = Log_Event(round(self.env.now, 2), "SOURCE_A", "SOURCE", "CREATE")
        record.add_sim_event(event_log)

    def source(self, env, number, interval, service_div):
        """Source generates opportunities randomly"""
        for i in range(number):
            opp = Opportunity(env, f'Opp{i}', service_div, time_in_queue=RES_A_TIME)
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

        # LOG OPP CREATE***********
        event_log = Log_Event(round(self.env.now, 2), name, "OPP", "CREATE")
        record.add_sim_event(event_log)

        yield env.timeout(10)  # ***temp delay before resource req for debug...remove later

        with service_div.request() as req:
            patience = random.uniform(MIN_PATIENCE, MAX_PATIENCE)
            # Wait for the Service team or abort at the end of our tether
            results = yield req | env.timeout(patience)

            wait = env.now - arrive  # Is this used???

            if req in results:
                # LOG OPP GET RESOURCE***********
                event_log = Log_Event(round(self.env.now, 2), name, "OPP", "RA_USE")
                record.add_sim_event(event_log)

                tib = random.expovariate(1.0 / time_in_queue)
                yield env.timeout(tib)

                # LOG OPP FINISH***********
                event_log = Log_Event(round(self.env.now, 2), name, "OPP", "RA_FINISH")
                record.add_sim_event(event_log)

            else:
                # LOG OPP RENEGE***********
                event_log = Log_Event(round(self.env.now, 2), name, "OPP", "RA_RENEGE")
                record.add_sim_event(event_log)

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
    def __init__(self, opp_info, location):
        super(OppEntity, self).__init__()
        self.info = opp_info
        self.time = opp_info.time
        self.name = opp_info.name
        self.type = opp_info.type
        self.action = opp_info.action
        self.location = location
        self.color = LIGHT_GREEN

        self.surf = pygame.Surface((50, 50), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(center=self.location)
        pygame.draw.polygon(self.surf, self.color, [(12, 0), (36, 0), (50, 25), (36, 50), (12, 50), (0, 25)])

        self.text = pygame.font.Font(None, 24).render(self.name, True, BLACK)
        self.text_rect = self.text.get_rect()
        self.text_rect.centerx = 50 // 2
        self.text_rect.bottom = 35
        self.surf.blit(self.text, self.text_rect)

        self.default_motion_rads = math.radians(random.randint(0, 360))
        self.motion_speed = 6

    def update(self, *args):
        cos_rads = math.cos(self.default_motion_rads)
        sin_rads = math.sin(self.default_motion_rads)
        self.rect.y += (self.motion_speed * sin_rads)
        self.rect.x += (self.motion_speed * cos_rads)

    def draw(self, color):
        pygame.draw.polygon(self.surf, color, [(12, 0), (36, 0), (50, 25), (36, 50), (12, 50), (0, 25)])
        self.surf.blit(self.text, self.text_rect)


class SourceEntity(pygame.sprite.Sprite):
    def __init__(self, source_info, location):
        super(SourceEntity, self).__init__()
        self.info = source_info
        self.time = source_info.time
        self.name = source_info.name
        self.type = source_info.type
        self.action = source_info.action
        self.location = location
        self.color = LIGHT_GRAY

        self.surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(center=self.location)
        pygame.draw.polygon(self.surf, self.color, [(0, 0), (100, 0), (50, 100)])

        self.text = pygame.font.Font(None, 18).render(self.name, True, BLACK)
        self.text_rect = self.text.get_rect()
        self.text_rect.centerx = 100 // 2
        self.text_rect.top = 5
        self.surf.blit(self.text, self.text_rect)


class ResourceEntity(pygame.sprite.Sprite):
    def __init__(self, resource_info, location):
        super(ResourceEntity, self).__init__()
        self.info = resource_info
        self.time = resource_info.time
        self.name = resource_info.name
        self.type = resource_info.type
        self.action = resource_info.action
        self.location = location
        self.color = LIGHT_BLUE

        self.surf = pygame.Surface((100, 100), pygame.SRCALPHA)
        self.rect = self.surf.get_rect(center=self.location)
        pygame.draw.ellipse(self.surf, self.color, self.surf.get_rect())

        self.text = pygame.font.Font(None, 18).render(self.name, True, BLACK)
        self.text_rect = self.text.get_rect()
        self.text_rect.centerx = 100 // 2
        self.text_rect.centery = 100 // 2
        self.surf.blit(self.text, self.text_rect)

class SIMScene(Scene):
    def __init__(self):
        super().__init__()
        print("VIZ Scene")

        # Obj Properties
        self.empty_deque = False

        # Locations for scene items
        self.scene_setup = {"SOURCE_A": (200, 200),
                            "RESOURCE_A": (1500, 300),
                            "END_LOC": (1500, 900)}

        # Dict of all scene sim entities by name
        self.scene_entity = {}

        # Sprite groups to control movement and collisions around static entities
        self.LOST_GROUP = pygame.sprite.Group()
        self.PLACED_GROUP = pygame.sprite.Group()

        # Scene Common Text
        self.title_text = pygame.font.Font(None, 64).render("SIM ALPHA", 1, WHITE)
        self.over_text = pygame.font.Font(None, 64).render("Queue Empty...OVER!!!", 1, RED)
        self.title_rect = self.title_text.get_rect()
        self.over_rect = self.over_text.get_rect()
        self.title_rect.centerx = SCREEN_WIDTH // 2
        self.title_rect.bottom = SCREEN_HEIGHT // 2
        self.over_rect.centerx = SCREEN_WIDTH // 2
        self.over_rect.bottom = (SCREEN_HEIGHT // 2) + 300

    def sim_create_resource(self, create_resource_event):
        if create_resource_event.name == "RESOURCE_A":
            new_resource = ResourceEntity(create_resource_event, self.scene_setup["RESOURCE_A"])
            self.PLACED_GROUP.add(new_resource)
            self.scene_entity[new_resource.name] = new_resource

    def sim_create_source(self, create_source_event):
        if create_source_event.name == "SOURCE_A":
            new_source = SourceEntity(create_source_event, self.scene_setup["SOURCE_A"])
            self.PLACED_GROUP.add(new_source)
            self.scene_entity[new_source.name] = new_source

    def process_sim_event(self):
        # Pop next event off queue
        next_sim_event = record.sim_queue.popleft()

        print(" ")
        pprint.pprint(next_sim_event)
        pprint.pprint(f'Game Time {pygame.time.get_ticks()} with SIM Time {next_sim_event.time * SIM_SPEED}')

        # Process each log event
        if (next_sim_event.type == "SOURCE") and (next_sim_event.action == "CREATE"):
            self.sim_create_source(next_sim_event)
        if (next_sim_event.type == "RESOURCE") and (next_sim_event.action == "CREATE"):
            self.sim_create_resource(next_sim_event)
        if (next_sim_event.type == "OPP") and (next_sim_event.action == "CREATE"):
            new_opp = OppEntity(next_sim_event, self.scene_setup["SOURCE_A"])
            self.LOST_GROUP.add(new_opp)
            self.scene_entity[new_opp.name] = new_opp
        if (next_sim_event.type == "OPP") and (next_sim_event.action == "RA_USE"):
            opp_obj = self.scene_entity.get(next_sim_event.name)
            self.LOST_GROUP.add(opp_obj)
            self.PLACED_GROUP.remove(opp_obj)
            opp_obj.rect.center = self.scene_setup.get("RESOURCE_A")
        if (next_sim_event.type == "OPP") and (next_sim_event.action == "RA_FINISH"):
            opp_obj = self.scene_entity.get(next_sim_event.name)
            self.LOST_GROUP.add(opp_obj)
            self.PLACED_GROUP.remove(opp_obj)
            opp_obj.rect.center = self.scene_setup.get("END_LOC")
            opp_obj.draw(WHITE)
        if (next_sim_event.type == "OPP") and (next_sim_event.action == "RA_RENEGE"):
            opp_obj = self.scene_entity.get(next_sim_event.name)
            opp_obj.draw(CHOCOLATE)

    def process_input(self, events, pressed_keys):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.terminate()

        queue_peek = len(record.sim_queue) > 0
        while queue_peek:
            if (record.sim_queue[0][0] * SIM_SPEED) <= pygame.time.get_ticks():
                self.process_sim_event()
                queue_peek = len(record.sim_queue) > 0
            else:
                queue_peek = False

        # Event queue empty, end viz
        if len(record.sim_queue) == 0:
            self.empty_deque = True

    def update(self):
        for opp_sprite in self.LOST_GROUP.sprites():
            if pygame.sprite.spritecollideany(opp_sprite, self.PLACED_GROUP):
                opp_sprite.update()
            else:
                self.LOST_GROUP.remove(opp_sprite)
                self.PLACED_GROUP.add(opp_sprite)

    def render(self):
        # Set background color
        SCREEN.fill(BLACK)

        # Render Text
        SCREEN.blit(self.title_text, self.title_rect)
        if self.empty_deque:
            SCREEN.blit(self.over_text, self.over_rect)

        # Render SIM Objects
        for entity in self.PLACED_GROUP:
            SCREEN.blit(entity.surf, entity.rect)
        for entity in self.LOST_GROUP:
            SCREEN.blit(entity.surf, entity.rect)

    def terminate(self):
        print("\nQueue Empty...OVER!!!")
        print("LOST:    ", self.LOST_GROUP)
        print("PLACED:  ", self.PLACED_GROUP)
        pprint.pprint(self.scene_entity)
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
    print('START VIZ SIM ALPHA......................')

    # RUN SIMULATION FIRST
    record = SIMObserver()
    opportunities = Source(env)
    print('SIM START')
    env.run()
    print('SIM OVER')
    record.print_deque()

    # RUN SIM VIZ
    print('VIZ START')
    first_scene = SIMScene()
    game_dir = Director(first_scene)
    game_dir.action()
    print('VIZ OVER')
    pygame.quit()
    print('END VIZ SIM ALPHA.........................')
    sys.exit()


