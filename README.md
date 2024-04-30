# CMPSC441 Final Project

I rewrote a lot of the code for this, copying applicable parts from the lab files when necessary, since there is a lot of code that is unnecessary for the final game and I want a cleaner enviroment.

I really overhauled a lot of the game's functionality. Sorry if this makes grading harder.

## Gameplay

Run `game.py` to play!

### World

On the World screen, your current location is represented by a blue city name. Your goal is to reach the destination city, marked by a yellow name. 
The colored lines represent safe roads between cities. You can travel freely between cities with road connections to one another, save for the destination city, which is always defended by the boss.

Click on a city to travel to it. If you travel to a city you don't have a road connection to, you will begin a combat encounter. The enemy's HP is determined by the distance you travel through unsafe forest, so try to find narrow gaps between cities!

### Combat

When you enter combat, you will be asked to select between 3 different attacks. Click on an option to select it!
You and your enemy will attack at the same time. Pay attention to how your attacks and those of your enemy interact, and try to learn patterns in how an enemy attacks you. Each encounter is different, so be ready to think on your feet!

If the enemy's HP falls to 0, you will proceed to your destination and gain 20 HP.

If your HP falls to 0, you will be sent back to the last city you were at. Keep trying to cross the forest, find a shorter path, or level up your character's HP by clearing easier encounters.

Need an assist? Activate the AI player by pressing `N` in combat! They've seen it all, so they can figure out the patterns in an enemy's behavior and respond appropriately.

## Technical Details

### World Generation

The terrain of the world is generated from simple Perlin noise, and a color map is applied to make it visually resemble land.

To place cities in realistic locations, I used a simple system. For each city I sample 32 random locations sampled evenly across the map.
Each location is then graded for its fitness as a location for a city. It must not be too high, or too low, and the further away it is from other cities the better.
A small incentive is placed towards avoiding the very edges of the map, to make the world map more neat. The location with the highest fitness value is selected as that city's location. This strikes a balance between total randomness and the complex approach taken with the genetic algorithm.

Routes are placed randomly between cities, with a maximum of 10.

### Enemy AI

Each time an encounter begins, a different enemy AI style is chosen. These styles are:

* Stubborn: Picks a single move at the start of the fight, and repeats it every time.
* Antsy: Makes whichever move would counter its last move. After ATTACK 2, it will play ATTACK 3, etc.
* Schemer: Makes a move and repeats it for 3 turns, before selecting a new move.
* Skipper: Makes whichever move would lose to its last move. After ATTACK 2, it will play ATTACK 1, etc.

These styles provide a relatively varied challenge for the player's pattern recognition, as well as the player AI's.

### Player AI

In combat, the player can ask a neural network to take over the fight. The neural network was made with PyTorch, and has two hidden layers.
It was trained on 20,000 sequences of enemy attacks to 40 epochs on my RTX 3080, with a batch size of 50. It can be retrained by running `neural.py` with a CUDA-compatible GPU installed. It takes a sequence of at most 20 enemy attacks and predicts the next attack.

I use a slightly biased (<0.3 = attack 1, >1.3 = attack 3, else attack 2) interpretation of model output data to add variety to behavior and prevent it from being biased towards attack 2.


### Pregenerated Worlds

To avoid long load times, the visual environment can be loaded from one of many pregenerated worlds. If `pregenerator.py` is not run, it will default to generating a new world every time.