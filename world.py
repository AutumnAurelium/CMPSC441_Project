import os
import random
import numpy as np
from cities import Cities
import pregenerator
import worldgen


class World:
    world_elevation: np.ndarray
    world_color: np.ndarray

    cities: Cities

    def __init__(self):
        if os.path.exists("pregen/world_0.pkl"): # If the pregenerator has been run, use a pregenerated world.
            world_num = random.randint(0, 99)
            print(f"Loading pregenerated world #{world_num}")
            self.world_elevation, self.world_color = pregenerator.load_world(world_num)
        else: # otherwise, generate a new one
            print(f"Generating a new world...")
            self.world_elevation = worldgen.get_elevation((640, 480))
            self.world_color = worldgen.elevation_to_rgba(self.world_elevation)

        # generate 10 random cities
        self.cities = Cities(self.world_elevation)