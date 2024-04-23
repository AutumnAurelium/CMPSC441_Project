import pickle
from typing import Tuple
import numpy as np
import worldgen
from multiprocessing import Pool

"""
I was tired of waiting so long at every game run, so I made this script which would pregenerate a large number of landscapes, from which we can choose randomly.
City gen would be different every time, anyway, so the game would play differently every time even on the same world.
"""

def generate_world(i: int):
    world_landscape = worldgen.get_elevation((640, 480))
    rgba = worldgen.elevation_to_rgba(world_landscape)
    with open(f"pregen/world_{i}.pkl", "wb") as f:
        pickle.dump(world_landscape, f)
    with open(f"pregen/world_{i}_rgba.pkl", "wb") as f:
        pickle.dump(rgba, f)
    print(f"Saved elevation to pregen/world_{i}.pkl")

def load_world(i: int) -> Tuple[np.ndarray, np.ndarray]:
    with open(f"pregen/world_{i}.pkl", "rb") as f:
        world_elevation = pickle.load(f)
    with open(f"pregen/world_{i}_rgba.pkl", "rb") as f:
        world_color = pickle.load(f)
    return world_elevation, world_color

if __name__ == "__main__":
    threads = []
    with Pool(10) as p:
        p.map(generate_world, range(100))
        
    for thread in threads:
        thread.join()