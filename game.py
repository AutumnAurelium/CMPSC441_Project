import math
import random
from typing import List, Tuple
import pygame

from combat import Combat
from neural import NeuralPlayer
from world import World

class GameState:
    screen: str
    world: World
    location: int

    combat: Combat

    def __init__(self):
        self.screen = "World"
        self.world = World()
        self.location = 0
        self.combat = Combat()

class Game:
    state: GameState
    running: bool
    screen: pygame.Surface
    screen_size: Tuple[int, int]

    # world map related
    landscape_surf: pygame.Surface

    # sprites
    player_sprite_idle: List[pygame.Surface]
    player_sprite_attack: List[List[pygame.Surface]]

    enemy_sprite_idle: List[pygame.Surface]
    enemy_sprite_attack: List[pygame.Surface]

    keyboard_prompts: pygame.Surface
    buttons_loc: List[Tuple[int, int]]

    # animations
    player_animation: str
    player_anim_timer: int
    player_anim_choice: int

    enemy_animation: str
    enemy_anim_timer: int
    enemy_anim_choice: int

    bg_animation_timer: int

    buttons_bb: List[Tuple[int, int, int, int]]
    button_choice: int

    # sounds
    sound_battle_start: pygame.mixer.Sound
    sound_win: pygame.mixer.Sound
    sound_lose: pygame.mixer.Sound
    sound_draw: pygame.mixer.Sound
    sound_battle_win: pygame.mixer.Sound
    sound_battle_lose: pygame.mixer.Sound

    # neural player
    enable_neural_player: bool
    neural_player: NeuralPlayer
    neural_player_move_timer: int

    def __init__(self):
        self.state = GameState()
        self.running = False

    def start(self):
        self.landscape_surf = pygame.surfarray.make_surface(self.state.world.world_color[:, :, :3])

        # Initialize Pygame
        pygame.init()

        # Set up the display
        self.screen_size = (640, 640)
        self.screen = pygame.display.set_mode(self.screen_size)

        pygame.mixer.init()
        pygame.mixer.music.load("assets/sound/mus_checkers.mp3")

        self.sound_battle_start = pygame.mixer.Sound("assets/sound/snd_battle_start.wav")
        self.sound_win = pygame.mixer.Sound("assets/sound/snd_win.wav")
        self.sound_lose = pygame.mixer.Sound("assets/sound/snd_lose.wav")
        self.sound_draw = pygame.mixer.Sound("assets/sound/snd_draw.wav")
        self.sound_battle_win = pygame.mixer.Sound("assets/sound/snd_battle_win.wav")
        self.sound_battle_lose = pygame.mixer.Sound("assets/sound/snd_battle_lose.wav")

        self.player_anim_timer = 0
        self.player_animation = "idle"
        self.player_anim_choice = 0

        self.enemy_anim_timer = 0
        self.enemy_animation = "idle"
        self.enemy_anim_choice = 0

        self.bg_animation_timer = 0

        self.keyboard_prompts = pygame.transform.scale(pygame.image.load("assets/sprites/keyboard_prompts.png"), (342*2, 192*2))
        self.buttons_loc = [(53*2, 132*2, 11*2, 11*2), (77*2, 132*2, 11*2, 11*2), (101*2, 132*2, 11*2, 11*2)]

        self.buttons_bb = [(15, 300, 11*2, 11*2), (45, 300, 11*2, 11*2), (75, 300, 11*2, 11*2)]
        self.button_choice = -1

        self.player_sprite_idle = []
        for i in range(3):
            img = pygame.image.load(f"assets/sprites/player/idle_{i+1}.png")
            size = img.get_size()
            self.player_sprite_idle.append(pygame.transform.scale(img, (size[0]*2, size[1]*2)))

        self.player_sprite_attack = []
        for weapon in range(3):
            frames = []
            for i in range(3):
                img = pygame.image.load(f"assets/sprites/player/attackWeapon{weapon+1}_{i+1}.png")
                size = img.get_size()
                frames.append(pygame.transform.scale(img, (size[0]*2, size[1]*2)))
            self.player_sprite_attack.append(frames)

        self.enemy_sprite_idle = []
        for i in range(3):
            img = pygame.image.load(f"assets/sprites/enemy/idle_{i+1}.png")
            size = img.get_size()
            self.enemy_sprite_idle.append(pygame.transform.scale(pygame.image.load(f"assets/sprites/enemy/idle_{i+1}.png"), (size[0]*2, size[1]*2)))

        self.enemy_sprite_attack = []
        for weapon in range(3):
            frames = []
            for i in range(3):
                img = pygame.image.load(f"assets/sprites/enemy/attackWeapon{weapon+1}_{i+1}.png")
                size = img.get_size()
                frames.append(pygame.transform.scale(img, (size[0]*2, size[1]*2)))
            self.enemy_sprite_attack.append(frames)
        
        self.enable_neural_player = False
        self.neural_player = NeuralPlayer()
        self.neural_player_move_timer = 0

        self.game_loop()

    def game_loop(self):
        # Game loop
        self.running = True
        while self.running:
            # Handle events
            self.handle_input()

            # Update game logic
            self.game_update()

            # Render graphics
            self.render()

            pygame.display.set_caption("CMPSC441 Final Project - " + self.state.screen)

            if self.state.screen == "Combat":
                if self.player_animation == "attack" and self.player_anim_timer > 120:
                    self.player_animation = "idle"
                    self.button_choice = -1
                    self.state.combat.turn = "enemy"
                
                self.player_anim_timer += 1

                if self.enemy_animation == "attack" and self.enemy_anim_timer > 130:
                    self.enemy_animation = "idle"
                    
                self.enemy_anim_timer += 1

                self.bg_animation_timer += 1

        # Close everything
        pygame.quit()

    def handle_input(self):
        city_manager = self.state.world.cities

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:
                    self.enable_neural_player = not self.enable_neural_player
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.state.screen == "World":
                    # check if we clicked on a city
                    for i, city in enumerate(city_manager.cities):
                        if ((city.location[0] - event.pos[0]) ** 2 + (city.location[1] - event.pos[1]) ** 2) ** 0.5 < 5:
                            # we clicked on a city

                            if i == self.state.location:
                                continue

                            distance = ((city_manager.cities[i].location[0] - city_manager.cities[self.state.location].location[0]) ** 2 + (city_manager.cities[i].location[1] - city_manager.cities[self.state.location].location[1]) ** 2) ** 0.5

                            if ((i, self.state.location) not in city_manager.routes and (self.state.location, i) not in city_manager.routes) or i == self.state.world.cities.goal_city:
                                self.state.screen = "Combat"
                                self.state.combat.battle_started(distance, self.state.world.cities.goal_city == i, i)

                                self.sound_battle_start.play()
                                pygame.mixer.music.play(-1)
                            else:
                                self.state.location = i
                                self.state.combat.last_outcome = "none"
                elif self.state.screen == "Combat":
                    if self.player_animation == "idle" and self.enemy_animation == "idle":
                        for i in range(3):
                            if self.buttons_bb[i][0] < event.pos[0] < self.buttons_bb[i][0] + self.buttons_bb[i][2] and self.buttons_bb[i][1] < event.pos[1] < self.buttons_bb[i][1] + self.buttons_bb[i][3]:
                                self.handle_combat_input(i)
                                break

    def handle_combat_input(self, i: int):
        self.button_choice = i
        self.player_animation = "attack"
        self.player_anim_timer = 0
        self.player_anim_choice = i

        # run combat
        result, enemy_move, battle_over = self.state.combat.run_turn(i)
        self.enemy_anim_choice = enemy_move
        self.enemy_animation = "attack"
        self.enemy_anim_timer = 0

        if result == "win":
            self.sound_win.play()
        elif result == "loss":
            self.sound_lose.play()
        elif result == "draw":
            self.sound_draw.play()

        if battle_over:
            self.state.screen = "World"
            pygame.mixer.music.stop()

            if self.state.combat.last_outcome == "win":
                self.state.location = self.state.combat.destination
                self.sound_battle_win.play()
            elif self.state.combat.last_outcome == "loss":
                self.sound_battle_lose.play()

        if self.state.combat.enemy_health <= 0:
            # player wins
            self.state.screen = "World"
            self.state.location = self.state.combat.destination
            self.state.combat.player_max_health += 20 # add reward
            self.sound_battle_win.play()
            pygame.mixer.music.stop()
        elif self.state.combat.player_health <= 0:
            # we lose
            self.state.screen = "World"
            self.sound_battle_lose.play()
            pygame.mixer.music.stop()

        print(result)
        print(self.state.combat.player_health, self.state.combat.enemy_health)
        print()

    def game_update(self):
        if self.state.screen == "World":
            if self.state.location == self.state.world.cities.goal_city:
                self.state.screen = "Victory"

        if self.enable_neural_player:
            self.neural_player_move_timer += 1

            if self.neural_player_move_timer > 150:
                self.neural_player_move_timer = 0
                if self.state.screen == "Combat" and self.player_animation == "idle" and self.enemy_animation == "idle":
                    move = (self.neural_player.predict(self.state.combat) + 1) % 3

                    self.handle_combat_input(move)

    def draw_text(self, text: str, x: int, y: int, font_size=20, color=(255, 255, 255), center=False):
        text_surface = pygame.font.SysFont(None, font_size).render(text, True, color)
        text_rect = text_surface.get_rect()
        if center:
            text_rect.center = (x, y)
        else:
            text_rect.topleft = (x, y)
        self.screen.blit(text_surface, text_rect)
        return text_rect.size

    def render(self):
        self.screen.fill((0, 0, 0))  # Fill the screen with black

        if self.state.screen == "World":
            self.draw_world()
        elif self.state.screen == "Combat":
            self.draw_combat()
        elif self.state.screen == "Victory":
            self.draw_text("You win!", 320, 320, center=True, font_size=50)
            self.draw_text(f"With your final enemy defeated, you proceed to {self.state.world.cities.cities[self.state.location].name}.", 320, 360, center=True)
            self.draw_text("As you enter the city, you are showered with gifts and praise for defeating the brute terrorizing it.", 320, 400, center=True)
            self.draw_text("Content with having saved the day, you prepare for your next adventure...", 320, 440, center=True)

        self.draw_ui()

        pygame.display.flip()  # Update the display

    def draw_world(self):
        city_manager = self.state.world.cities

        self.screen.blit(self.landscape_surf, (0, 0))

        for route in city_manager.routes:
            pygame.draw.line(self.screen, route[2], city_manager.cities[route[0]].location, city_manager.cities[route[1]].location, 3)

        for i, city in enumerate(city_manager.cities):
            pygame.draw.circle(self.screen, (255, 0, 0), city.location, 5)

            # draw text
            color = (255, 255, 255)
            size = 20
            if i == city_manager.goal_city:
                color = (255, 255, 0)
                size = 25
            elif i == self.state.location:
                color = (0, 255, 255)
                size = 25
            
            self.draw_text(city.name, city.location[0], city.location[1] + 10, color=color, font_size=size)

    def draw_combat(self):
        # draw weird pillar things
        odd_pillar_color = (100, 100, 150)
        even_pillar_color = (100, 100, 100)
        pillar_count = 16
        if self.enable_neural_player:
            odd_pillar_color = (100, 150, 100)

        if self.state.combat.is_boss:
            pillar_count = 32

        if self.state.combat.last_outcome == "win":
            even_pillar_color = (100, 200, 100)
        elif self.state.combat.last_outcome == "loss":
            even_pillar_color = (200, 100, 100)
        
        for i in range(pillar_count):
            pygame.draw.rect(
                self.screen,
                even_pillar_color if i%2==0 else odd_pillar_color,
                (
                    i*(640 // pillar_count),
                    80 + 80 * math.sin(self.bg_animation_timer / 80.0 + i*40),
                    600 // pillar_count,
                    400
                )
                )

        # draw player
        player_loc = (0, 320)
        if self.player_animation == "idle":
            self.screen.blit(self.player_sprite_idle[self.player_anim_timer // 80 % 3], player_loc)
        elif self.player_animation == "attack":
            sprite = self.player_sprite_attack[self.player_anim_choice][self.player_anim_timer // 40 % 3]
            if self.player_anim_timer > 120: # hang on last frame for a bit
                sprite = self.player_sprite_attack[self.player_anim_choice][-1]
            self.screen.blit(sprite, player_loc)
        
        # draw health bar
        health_percent = self.state.combat.player_health / self.state.combat.player_max_health
        pygame.draw.rect(self.screen, (255, 0, 0), (15, 280, 81 * health_percent, 10))

        # draw health value above bar
        self.draw_text(f"{self.state.combat.player_health}/{self.state.combat.player_max_health}", 50, 270, font_size=15)

        # draw controls
        for i in range(3):
            loc = self.buttons_loc[i]
            if self.button_choice == i:
                loc = (loc[0] + 22, loc[1], loc[2], loc[3])
            self.screen.blit(self.keyboard_prompts, (self.buttons_bb[i][0], self.buttons_bb[i][1]), loc)

        # draw enemy
        enemy_loc = (440, 260)
        if self.enemy_animation == "idle":
            self.screen.blit(self.enemy_sprite_idle[self.enemy_anim_timer // 80 % 3], enemy_loc)
        elif self.enemy_animation == "attack":
            sprite = self.enemy_sprite_attack[self.enemy_anim_choice][self.enemy_anim_timer // 40 % 3]
            if self.enemy_anim_timer > 120: # hang on last frame for a bit
                sprite = self.enemy_sprite_attack[self.enemy_anim_choice][-1]
            self.screen.blit(sprite, enemy_loc)
        
        # draw health bar
        health_percent = self.state.combat.enemy_health / self.state.combat.enemy_max_health
        color = (255, 0, 0)
        if self.state.combat.is_boss:
            color = (255, 255, 0)
        pygame.draw.rect(self.screen, color, (480 + 15, 280, 81 * health_percent, 10))

        # draw health value above bar
        self.draw_text(f"{self.state.combat.enemy_health}/{self.state.combat.enemy_max_health}", 480 + 50, 270, font_size=15)

    def draw_ui(self):
        city_manager = self.state.world.cities
        if self.state.screen == "World":
            self.draw_text("Travelling", 20, 500, font_size=30)
            self.draw_text(f"Objective: Get to {city_manager.cities[city_manager.goal_city].name}", 20, 520)
            if self.state.combat.last_outcome == "win":
                self.draw_text(f"Victory! You defeated the enemy and gained 20 health, proceeding to {self.state.world.cities.cities[self.state.location].name}", 20, 540)
            elif self.state.combat.last_outcome == "loss":
                self.draw_text(f"Defeat! You barely managed to escape back to {self.state.world.cities.cities[self.state.location].name}...", 20, 540)
        elif self.state.screen == "Combat":
            if self.state.combat.is_boss:
                self.draw_text("Final Encounter!", 20, 500, font_size=30)
                self.draw_text("As you neared your destination, a powerful enemy emerged and attacked you!", 20, 520)
            else:
                self.draw_text("Combat!", 20, 500, font_size=30)
                self.draw_text("As you trekked through the wilderness, you were attacked!", 20, 520)
            
            if self.enable_neural_player:
                self.draw_text("AI is enabled! Press N to disable", 20, 560)

            latest = self.state.combat.history[-1] if len(self.state.combat.history) > 0 else (None, None, None)

            if latest[2] == "win":
                self.draw_text(f"Your ATTACK {latest[0]+1} breaks through the enemy's ATTACK {latest[1]+1}, causing 20 damage!", 20, 540)
            elif latest[2] == "loss":
                self.draw_text(f"The enemy's ATTACK {latest[1]+1} breaks through your ATTACK {latest[0]+1}, causing 20 damage!", 20, 540)
            elif latest[2] == "draw":
                self.draw_text(f"Both of your ATTACK {latest[1]+1}s clash together, dealing no damage!", 20, 540)
            else:
                self.draw_text("Choose your attack!", 20, 540)

if __name__ == "__main__":
    game = Game()
    game.start()