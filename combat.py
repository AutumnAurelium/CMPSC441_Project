import random
from typing import List, Tuple


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

    def __init__(self) -> None:
        self.player_health = 100
        self.player_max_health = 100
        self.enemy_health = 100
        self.enemy_max_health = 100
        self.is_boss = False
        self.destination = -1
        self.last_outcome = "none"
        self.enemy_strategy = "random"

        self.history = []

    def battle_started(self, distance: int, is_boss: bool, destination: int) -> None:
        self.is_boss = is_boss
        if is_boss:
            self.enemy_health = 500 + round(distance)
        else:
            self.enemy_health = round(distance / 2)
        
        self.enemy_max_health = self.enemy_health
        self.history = []
        self.enemy_strategy = random.choice(["stubborn", "antsy", "schemer", "skipper"])
        self.destination = destination
        self.player_health = self.player_max_health

    # wrapper for run_turn that also handles learning
    # if enemy_move is specified it lets you bypass the enemy move selector
    def run_turn(self, player_move: int, enemy_move=None) -> Tuple[str, int, bool]:
        outcome = ""
        if enemy_move is None:
            enemy_move = self.select_enemy_move()

        if player_move == enemy_move:
            outcome = "draw"
        elif (player_move + 1) % 3 == enemy_move:
            self.player_health -= 20
            outcome = "loss"
        else:
            self.enemy_health -= 20
            outcome = "win"

        self.history.append((player_move, enemy_move, outcome))

        self.last_outcome = outcome

        return outcome, enemy_move, (self.player_health <= 0 or self.enemy_health <= 0)

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