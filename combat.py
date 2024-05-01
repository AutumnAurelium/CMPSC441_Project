import random
from typing import List, Tuple

import numpy as np

from world import World


class Combat:
    destination: int

    player_health: int
    player_max_health: int

    enemy_health: int
    enemy_max_health: int

    is_boss: bool

    last_outcome: str

    enemy_strategy: str

    history: List[Tuple[int, int, str]]

    heals_remaining: int
    added_heal: bool

    def __init__(self) -> None:
        self.player_health = 100
        self.player_max_health = 100
        self.enemy_health = 100
        self.enemy_max_health = 100
        self.is_boss = False
        self.destination = -1
        self.last_outcome = "none"
        self.enemy_strategy = "random"
        self.heals_remaining = 5
        self.added_heal = False

        self.history = []

    def battle_started(self, location: int, destination: int, world: World) -> None:
        self.is_boss = world.cities.goal_city == destination
        if world != None:
            self.enemy_health = self.calculate_enemy_health(location, destination, world)
        else: # for simulating without a full game state in the neural network training
            self.enemy_health = 100
        self.enemy_max_health = self.enemy_health
        self.history = []
        self.enemy_strategy = random.choice(["stubborn", "antsy", "schemer", "skipper"])
        self.destination = destination
        self.player_health = self.player_max_health

    def calculate_enemy_health(self, city_1: int, city_2: int, world: World) -> int:
        is_boss = world.cities.goal_city == city_2
        city_1_pos = world.cities.cities[city_1].location
        city_2_pos = world.cities.cities[city_2].location

        number_of_points=30
        xs=np.linspace(city_1_pos[0],city_2_pos[0],number_of_points+2)
        ys=np.linspace(city_1_pos[1],city_2_pos[1],number_of_points+2)

        total_elevation = 0
        for i in range(len(xs)):
            total_elevation += world.world_elevation[int(xs[i]), int(ys[i])]
        
        distance = ((city_1_pos[0] - city_2_pos[0]) ** 2 + (city_1_pos[1] - city_2_pos[1]) ** 2) ** 0.5

        if is_boss:
            return 500 + int(total_elevation * 20)
        else:
            return round(int(total_elevation) * (distance / 20))

    def has_encounter(self, city_1: int, city_2: int, world: World) -> bool:
        if city_1 == city_2:
            return False
        has_road = False

        # if there is no route
        for start, end, color in world.cities.routes:
            if (start == city_1 and end == city_2) or (start == city_2 and end == city_1):
                if city_2 != world.cities.goal_city:
                    has_road = True
                    break
        
        return not has_road

    def calculate_damage(self, health: int) -> int:
        return health // 10

    # if enemy_move is specified it lets you bypass the enemy move selector
    def run_turn(self, player_move: int, enemy_move=None) -> Tuple[str, int, bool]:
        outcome = ""
        if enemy_move is None:
            enemy_move = self.select_enemy_move()

        if player_move == enemy_move:
            outcome = "draw"
        elif (player_move + 1) % 3 == enemy_move:
            self.player_health -= self.calculate_damage(self.enemy_max_health)
            outcome = "loss"
        else:
            self.enemy_health -= self.calculate_damage(self.player_max_health)
            outcome = "win"

        self.history.append((player_move, enemy_move, outcome))

        self.last_outcome = outcome

        self.added_heal = False

        if self.player_health <= 0: # player loses
            self.heals_remaining -= 1
        elif self.enemy_health <= 0: # player wins
            # handle healing
            if random.randint(0, 2) == 0:
                self.heals_remaining += 1
                self.added_heal = True
            
            # give health increase
            self.player_max_health += self.enemy_max_health // 10
        else:
            return outcome, enemy_move, False

        return outcome, enemy_move, True

    def select_enemy_move(self) -> int:
        if self.enemy_strategy == "stubborn": # picks an attack and uses it every time
            if len(self.history) == 0:
                return random.randint(0, 2)
            else:
                return self.history[-1][1]
        elif self.enemy_strategy == "antsy": # changes move to the next one every turn
            if len(self.history) == 0:
                return random.randint(0, 2)
            else:
                return (self.history[-1][1] + 1) % 3
        elif self.enemy_strategy == "schemer": # picks a move and uses it for 3 turns, before picking another move
            if len(self.history) == 0:
                return random.randint(0, 2)
            else:
                if len(self.history) % 3 == 0:
                    return random.randint(0, 2)
                else:
                    return self.history[-1][1]
        elif self.enemy_strategy == "skipper": # same as antsy, but skips a move
            if len(self.history) == 0:
                return random.randint(0, 2)
            else:
                return (self.history[-1][1] + 2) % 3
        else:
            print("Invalid attack pattern chosen:", self.enemy_strategy)
            return 0