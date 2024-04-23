import random
import numpy as np

import pregenerator
import worldgen

class World:
    world_elevation: np.ndarray
    world_color: np.ndarray

    def __init__(self, use_pregenerated=True):
        if use_pregenerated:
            self.world_elevation, self.world_color = pregenerator.load_world(random.randint(0, 99))
        else:
            self.world_elevation = worldgen.get_elevation((640, 480))
            self.world_color = worldgen.elevation_to_rgba(self.world_elevation)

class GameState:
    world: World

    def __init__(self):
        self.world = World()