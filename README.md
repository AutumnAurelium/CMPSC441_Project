# CMPSC441 Final Project

I rewrote a lot of the code to make the final game more fun and the code more well-structured, copying applicable parts from the lab files when necessary.

I really overhauled a lot of the game's functionality while sticking to the requirements. Sorry if this makes grading harder.

## Abstract

This project is an example of a game that poses a moderate challenge to both human players and AI agents. It can be played fully autonomously, or manually by the player.

The player is placed in a random city (marked in blue) on a procedurally-generated world map and given instructions to make their way to the goal city, marked in yellow. Traversing roads costs money, and travelling off of beaten paths results in enemy encounters. Both cost and enemy HP scale with the total elevation that must be traversed, so both distance and terrain matter. If you run out of money while travelling, you lose the game.

In combat, the player is prompted to choose between one of three possible attacks. The player and enemy will attack at the same time, and the result can either be a win for the player, a draw, or a loss for the player (following rock/paper/scissors rules). Whoever loses takes damage depending on the attacker's maximum HP.

If the player loses an encounter, they will lose a life. If all of their lives are lost, they lose the game. If the player wins an encounter, they are rewarded with increased maximum HP, as well as money and the chance to regain a life.

When travelling to the final city, regardless of whether a road was taken to get there, the player will face the final boss, with a great deal of health and a high attack. Upon defeating the boss, they win the game.

These rules provide an interesting challenge for both human players and AI agents, incentivizing complex behavior rather than finding shortcuts and exploits. The AI agent player works well with these rules, beating the game consistently.

## List of AI techniques

- Simple reflex agent (for Enemy AI and AI Player World Navigation)
- Utility-based agent (for City Selection)
- Model-based, reflex-based (for AI Player Combat)

## Problems Solved

- Enemy AI - The enemy AI is intentionally simplistic, consisting of a number of semi-predictable strategies for the player an AI player to learn. These strategies do not rely on any game state except for the enemy's previous responses, and return a single attack each turn. The chosen enemy strategy is not visible to the AI player or normal player, and must be figured out from patterns in the enemy's attacks.
    - Stubborn: This strategy picks an attack and uses it every time. If it's the first move (i.e., the history is empty), it selects a random move. Otherwise, it repeats the last move from the history.

    - Antsy: This strategy changes the move to the next one every turn. If it's the first move, it selects a random move. Otherwise, it increments the last move from the history by 1 (modulo 3, to ensure the result is within the range 0-2).

    - Schemer: This strategy picks a move and uses it for 3 turns, before picking another move. If it's the first move or the length of the history is a multiple of 3, it selects a random move. Otherwise, it repeats the last move from the history.

    - Skipper: This strategy is similar to the "Antsy" strategy, but it skips a move. If it's the first move, it selects a random move. Otherwise, it increments the last move from the history by 2 (modulo 3, to ensure the result is within the range 0-2).
- City Selection - The location of cities on the map is determined by a genetic algorithm, which trains on a fitness function designed to encourage even spacing, create realistic elevation placement, and prevent cities from spawning on the very edge of the map. It takes in an elevation matrix and returns 10 ideal city locations.
- AI Player (World Navigation) - The AI player follows a set of pre-programmed rules for navigating the world map. These rules, while simplistic, result in a great deal of game knowledge. Making a beeline directly to the target city leads to an encounter with a boss which, due to the distance involved, will easily have over 10x the player's health, and as such this course of action will never be judged "beatable" and be avoided. The player will naturally "grind" enemies and move around the map until it is powerful enough, and close enough to the final boss to be able to complete the encounter. It takes in the predicted health of every potential enemy encounter, a list of safe roads, and the player's current maximum health, and returns a city to travel to.
    1. Its actions should be split evenly between taking safe roads (which cost money) and unsafe routes (which cause an enemy encounter).
    2. When fighting, it should fight the most powerful enemy that is judged to be beatable (less than 110% of the player's health), since stronger enemies give more health, attack, and money when defeated.
- AI Player (Combat) - In combat, the AI player uses a custom-trained neural network. It takes the preceding 10 moves and predicts the next enemy move, allowing the AI player to counter it. The network was trained on 20,000 sequences of enemy attack patterns from a mix of all four enemy strategies.

The two AI player techniques result in an agent that will reliably kill increasingly powerful enemies for health, attack power, and money until it reaches a level where it can beat the final boss encounter.

## Appendix

I did not use any LLMs for this assignment, but I did use a number of sound effects. All sound effects and music are from DELTARUNE.