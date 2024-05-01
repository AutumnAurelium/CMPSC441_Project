import math
import random
from typing import Any, Callable, List, Tuple
import numpy as np
import pygad

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

    def __init__(self, elevation: np.ndarray, num_routes=10):
        fitness = lambda ga, solution, idx: self.game_fitness(
            solution, idx, elevation, (640, 480)
        )
        ga_instance = self.setup_GA(fitness, 10, (640, 480))

        ga_instance.run()

        best_solution = ga_instance.best_solution()[0]
        city_locs = self.solution_to_cities(best_solution, (640, 480))

        self.cities = []
        for i, city in enumerate(city_locs):
            self.cities.append(City(city_names[i], city))
        
        self.routes = []
        for i in range(num_routes):
            city1 = random.randint(0, len(self.cities)-1)
            city2 = random.randint(0, len(self.cities)-1)
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            self.routes.append((city1, city2, color))

        self.goal_city = random.randint(1, len(self.cities)-1)

    def setup_GA(self, fitness: Any, n_cities: int, size: Tuple[int, int]) -> pygad.GA:
        num_generations = 100
        num_parents_mating = 10

        solutions_per_population = 300
        num_genes = n_cities

        init_range_low = 0
        init_range_high = size[0] * size[1]

        parent_selection_type = "sss"
        keep_parents = 10

        crossover_type = "single_point"

        mutation_type = "random"
        mutation_percent_genes = 10

        ga_instance = pygad.GA(
            num_generations=num_generations,
            num_parents_mating=num_parents_mating,
            fitness_func=fitness,
            sol_per_pop=solutions_per_population,
            num_genes=num_genes,
            gene_type=int,
            init_range_low=init_range_low,
            init_range_high=init_range_high,
            parent_selection_type=parent_selection_type,
            keep_parents=keep_parents,
            crossover_type=crossover_type,
            mutation_type=mutation_type,
            mutation_percent_genes=mutation_percent_genes,
        )

        return ga_instance

    def solution_to_cities(self, solution, size: Tuple[int, int]):
        """
        It takes a GA solution and size of the map, and returns the city coordinates
        in the solution.

        :param solution: a solution to GA
        :param size: the size of the grid/map
        :return: The cities are being returned as a list of lists.
        """
        cities = np.array(
            list(map(lambda x: [int(x / size[0]), int(x % size[1])], solution))
        )
        return cities

    def game_fitness(self, solution, idx, elevation, size):
        fitness = 0.0001  # Do not return a fitness of 0, it will mess up the algorithm.
        """
        Create your fitness function here to fulfill the following criteria:
        1. The cities should not be under water
        2. The cities should have a realistic distribution across the landscape
        3. The cities may also not be on top of mountains or on top of each other
        """

        city_coords = self.solution_to_cities(solution, size)

        fitness_scores = []

        for location in city_coords:
            fitness = 0

            cur_elev = elevation[location[0], location[1]]
            if cur_elev < 0.9: # don't put cities on mountaintops
                fitness += 100
            if cur_elev > 0.3: # don't put cities underewater
                fitness += 300

            # distance to all other cities
            distance_to_others = [((location[0] - other[0]) ** 2 + (location[1] - other[1]) ** 2) ** 0.5 for other in city_coords]
            closest_distance = 0
            if len(distance_to_others) >= 1:
                closest_distance = min(distance_to_others)
            else:
                closest_distance = 1000

            # disincentivize having cities too close together
            fitness += (10000 / (closest_distance+0.1))

            # disincentivize having cities too close to the edge of the map
            if location[0] < 10 or location[0] > size[0] - 10 or location[1] < 10 or location[1] > size[1] - 10:
                fitness = 1

            fitness_scores.append(fitness)

        return sum(fitness_scores)