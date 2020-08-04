# Description
My very own Snake game implemented in OpenAI Gym. There are many out there, but there's none like this. :D
I'm a control freak so I like to have control over the environment itself, thus created this for education and flexibility.

This is the version v1. Snake v0 returns a set of observables while this version returns the entire environment. 

# Details
## How does the game works?
Standard Snake game. If you owned a Nokia phone ever, you would have played this game. 

## Source
TODO

## Observations
Entire environment in matrices.

## Actions
0 - Up
1 - Right
2 - Down
3 - Left

Pressing the movement while in the same direction yields no action. 
For example, if the snake is facing North, press Up will effectively do nothing.

## Reward System
- No reward?

## Starting State:
Snake starts at a random position within a given boundary
Apple appears at a random position throughout accessible positions in the environment. Changes position whenever it gets eaten.

## Episode Termination:
Snake collides with wall or itself.