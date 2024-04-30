import random
from typing import List, Tuple
import numpy as np

city_names = [
    "Morkomasto",
    "Morathrad",
    "Eregailin",
    "Corathrad",
    "Eregarta",
    "Numensari",
    "Rhunkadi",
    "Londathrad",
    "Baernlad",
    "Forthyr",
]

class City:
    name: str
    location: Tuple[int, int]

    def __init__(self, name: str, location: Tuple[int, int]):
        self.name = name
        self.location = location

class Cities:
    cities: List[City]
    routes: List[Tuple[int, int, Tuple[int, int, int]]]
    goal_city: int

    def __init__(self, elevation: np.ndarray, num_cities=len(city_names), locations_to_check=32, num_routes=10):
        self.cities = []
        for i in range(num_cities):
            location = self.find_suitable_location(elevation, locations_to_check)
            # theoretically we support having more cities than there are names, but there will be duplicates
            self.cities.append(City(city_names[i % len(city_names)], location))
        
        self.routes = []
        for i in range(num_routes):
            city1 = random.randint(0, len(self.cities)-1)
            city2 = random.randint(0, len(self.cities)-1)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.routes.append((city1, city2, color))

        self.goal_city = random.randint(1, len(self.cities)-1)

    # this is a compromise in complexity between completely random city locations and the genetic algorithm
    # we generate some number of possible locations and pick the best one
    def find_suitable_location(self, world_elevation: np.ndarray, locations_to_check: int) -> Tuple[int, int]:
        # generate a number of random locations
        locations = [(np.random.randint(0, 640), np.random.randint(0, 480)) for _ in range(locations_to_check)]

        fitness_scores = []

        for location in locations:
            fitness = 0

            elevation = world_elevation[location[0], location[1]]
            if elevation < 0.9: # don't put cities on mountaintops
                fitness += 100
            if elevation > 0.3: # don't put cities underewater
                fitness += 300

            # distance to all other cities
            distance_to_others = [((location[0] - other.location[0]) ** 2 + (location[1] - other.location[1]) ** 2) ** 0.5 for other in self.cities]
            closest_distance = 0
            if len(distance_to_others) >= 1:
                closest_distance = min(distance_to_others)
            else:
                closest_distance = 1000

            # disincentivize having cities too close together
            fitness += (10000 / closest_distance)

            # disincentivize having cities too close to the edge of the map
            fitness += 1000 / max(min(location[0], 640 - location[0], location[1], 480 - location[1]), 1)

            fitness_scores.append(fitness)
        
        # get most fit location of the sampled ones
        best_location = locations[np.argmin(fitness_scores)]

        return best_location

    def location_fitness(self, elevation: np.ndarray, location: Tuple[int, int]) -> float:
        pass