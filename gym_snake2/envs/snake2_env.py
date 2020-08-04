import gym
from gym import error, spaces, utils
from gym.utils import seeding

import pygame
import random
import numpy as np
import math

# Global parameters
MAX_SNAKE_HEALTH = 100

class SnakeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, render=False,segment_width=50):
        self.ENV_HEIGHT = 20 
        self.ENV_WIDTH = 20
        self.action_space = spaces.Discrete(4)
        self.snake_previous = None
        self.SEGMENT_WIDTH = segment_width # For rendering only
        self.RENDER = render

        # Render using pygame
        if render:
            self.window = pygame.display.set_mode((self.ENV_HEIGHT * self.SEGMENT_WIDTH, self.ENV_WIDTH * self.SEGMENT_WIDTH))

    def step(self, action):
        reward = 0 # initialize per step
        opp_facing = (self.facing + 2) % 4 # Calculate opposite of facing
        # If direction and action is NOT the same and not opposite of current direction facing
        if action != self.facing and action != opp_facing:
            # Update the new snake direction
            self.facing = action   
 
        #* Advancing the snake
        self._move_snake()
        self.done = self._check_collision()
        if self.done:
            reward += 0 # assigning negative reward not useful

        #* Consuming apple + growing
        #Simple Reward: Eating apple (1 point)
        if self._check_eaten():
            reward += 1
            self.snake_health = MAX_SNAKE_HEALTH # Health restored to max 
        #* Starving the snake
        else:
            self.snake_health -= 1 # reduce hitpoint simulate hunger.

        if self.snake_health == 0: 
            self.done = True
            print("debug: Snake starved to death. :(")

        #* Additional reward for moving closer towards the red apple
        if self.snake_previous:
            # Distance between 
            if all(abs(np.subtract(self.apple_pos, self.snake_segments[0])) <= abs(np.subtract(self.apple_pos, self.snake_previous))):
                reward += 0.01 # Surviving reward

        #* Final adjustments
        self.snake_previous = self.snake_segments[0]
        
        # State: 4 x collision (True/False), 4 x Snake Facing Direction (True/False), 4 x relative apple position (True/False), 1 x distance to apple (closer = higher value approaching 1, else approaching 0), 1 x if apple eaten this step
        #* Experimental Observations
        '''
        up_collision, right_collision, down_collision, left_collision = self._next_step_collision()
        #face_up, face_right, face_down, face_left = self._facing_direction()
        apple_above, apple_right, apple_below, apple_left = self._food_relative_direction()
        distance_to_apple = self._distance_to_apple()
        '''

        return None, None, self.done, {}

    #* Return a presentation of the board in numpy array
    def _get_board(self):
        '''
        -1 = Walls, Snake (deadly collide-able)
        0  = Nothing
        1  = Apple
        '''
        #* Create an np array initialize it to all 0
        board = np.full((self.ENV_WIDTH, self.ENV_HEIGHT), 0)
        
        #* Mark all the walls (-1)
        # Northern & Southern
        
        for j in range(0,self.ENV_WIDTH):
            board[0][j] = -1
            board[self.ENV_HEIGHT-1][j] = -1
        
        # Eastern & Western
        for i in range(0, self.ENV_HEIGHT):
            board[i][0] = -1
            board[i][self.ENV_WIDTH-1] = -1
        
        #* Place snake (-1)
        for segment in self.snake_segments:
            board[segment[1]][segment[0]] = -1

        #* Place apple (1)
        board[self.apple_pos[1]][self.apple_pos[0]] = 1

        return board


    def reset(self):
        # Snake starting position
        #TODO randomize starting
        self.snake_segments = [(15,15),(15,16),(15,17)]
        self.snake_health = MAX_SNAKE_HEALTH # Hitpoints
        self.facing = 0 # 0 is up, 1 is right, 2 is down, 3 is left #TODO randomize
        # Apple starting position
        self.apple_pos = self._spawn_apple()

        # 'Done' state
        self.done = False
  
        return #? need to return state?

    def render(self, mode='human', close=False):
        if not self.render:
            print("[!] Error rendering. Disable during object instantiation.")
            return
        #* Draw & Display
        self.window.fill((0,0,0)) # Clear screen to color black again

        # Walls
        for j in range(self.ENV_WIDTH):
            pygame.draw.rect(self.window, (90,90,5), (0, j*self.SEGMENT_WIDTH , self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))
            pygame.draw.rect(self.window, (90,90,5), ((self.ENV_HEIGHT-1)*self.SEGMENT_WIDTH, j*self.SEGMENT_WIDTH , self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))

        for i in range(self.ENV_HEIGHT):
            pygame.draw.rect(self.window, (90,90,5), (i*self.SEGMENT_WIDTH, 0 , self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))
            pygame.draw.rect(self.window, (90,90,5), (i*self.SEGMENT_WIDTH, (self.ENV_WIDTH-1)*self.SEGMENT_WIDTH , self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))

        # Snake head
        pygame.draw.rect(self.window, (25,135,75), (self.snake_segments[0][0]*self.SEGMENT_WIDTH, self.snake_segments[0][1]*self.SEGMENT_WIDTH, self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))

        # Snake body
        for segment in self.snake_segments[1:]:
            pygame.draw.rect(self.window, (25,205,75), (segment[0]*self.SEGMENT_WIDTH, segment[1]*self.SEGMENT_WIDTH, self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))
        
        # Apple
        pygame.draw.rect(self.window, (205,25,25), (self.apple_pos[0]*self.SEGMENT_WIDTH, self.apple_pos[1]*self.SEGMENT_WIDTH, self.SEGMENT_WIDTH, self.SEGMENT_WIDTH))
        pygame.display.update()
            
        return
    
    # Move the snake by 1 box / square
    def _move_snake(self):
        snake_head = (0,0)
        if self.facing == 0:
            snake_head = np.subtract(self.snake_segments[0], (0, 1))
        elif self.facing == 1:
            snake_head = np.add(self.snake_segments[0], (1, 0))
        elif self.facing == 2:
            snake_head = np.add(self.snake_segments[0], (0, 1))
        else:
            snake_head = np.subtract(self.snake_segments[0], (1, 0))

        leftovers = self.snake_segments[:-1]
        self.snake_segments = [] #reset
        self.snake_segments.append(tuple(snake_head))
        for segment in leftovers:
            self.snake_segments.append(segment)

        #debug 
        #print("_move_snake()::self.snake_segments (new snake):", self.snake_segments)

    def _check_collision(self, snake_head=None):
        if np.all(snake_head) == None: 
            snake_head = self.snake_segments[0]

        # Borders
        if snake_head[0] == self.ENV_HEIGHT-1 or snake_head[1] == self.ENV_WIDTH-1 or \
            snake_head[0] == 0 or snake_head[1] == 0:
            return 1

        # Snake itself
        for segment in self.snake_segments[1:]:
            if self.snake_segments[0] == segment:
                return 1

        return 0

    def _check_eaten(self):
        if self.snake_segments[0] == self.apple_pos:
            pass 
            #print("[+] NOM!") #debug
        else:
            return 0

        #* Growing the snake
        additional_segment = self.snake_segments[len(self.snake_segments)-1:] #select the last segment

        if self.facing == 0: 
            additional_segment = np.add(additional_segment, (0, 1))
        if self.facing == 1:
            additional_segment = np.subtract(additional_segment, (1, 0))
        if self.facing == 2:
            additional_segment = np.subtract(additional_segment, (0, 1))
        if self.facing == 3:
            additional_segment = np.add(additional_segment, (1, 0))
        
        self.snake_segments.append(tuple(additional_segment[0]))

        #* Respawn Apple at random location
        self.apple_pos = self._spawn_apple()

        return 1
   
    def _spawn_apple(self):
        while True:
            apple_position = (random.randrange(0,self.ENV_WIDTH), random.randrange(0,self.ENV_HEIGHT))

            # Ensure it does not spawn within the wall
            if apple_position[0] == 0 or apple_position[0] == self.ENV_WIDTH-1 or apple_position[1] == 0 or apple_position[1] == self.ENV_HEIGHT-1:
                continue
            # Ensure it does not spawn in any parts of the snake
            for segment in self.snake_segments:
                if np.all(segment == apple_position):
                    continue 

            return apple_position

    #* Observation Functions
    # Snake 
    #? May not be required for this version
    '''
    def _next_step_collision(self):
        # snake_segments[0] is the head of the snake

        # UP
        new_snake_head_pos = np.subtract(self.snake_segments[0], (0, self.SEGMENT_WIDTH))
        up_collision = self._check_collision(new_snake_head_pos)

        # RIGHT
        new_snake_head_pos = np.add(self.snake_segments[0], (self.SEGMENT_WIDTH, 0))
        right_collision = self._check_collision(new_snake_head_pos)

        # DOWN
        new_snake_head_pos = np.add(self.snake_segments[0], (0, self.SEGMENT_WIDTH))
        down_collision = self._check_collision(new_snake_head_pos)

        # LEFT
        new_snake_head_pos = np.subtract(self.snake_segments[0], (self.SEGMENT_WIDTH, 0))
        left_collision = self._check_collision(new_snake_head_pos)

        return up_collision, right_collision, down_collision, left_collision
    
    def _facing_direction(self):
        face_up = face_right = face_down = face_left = 0

        if self.facing == 0:
            face_up = 0
        if self.facing == 1:
            face_right = 1
        if self.facing == 2:
            face_down = 2
        if self.facing == 3:
            face_left = 3

        return face_up, face_right, face_down, face_left 

    # From current position, where is the food? Above, right, left or below
    def _food_relative_direction(self):
        apple_above = apple_right = apple_below = apple_left = 0

        # Above
        if self.apple_pos[1] < self.snake_segments[0][1]:
            apple_above = 1

        # Right of 
        if self.apple_pos[0] > self.snake_segments[0][0]:
            apple_right = 1 

        # Below - apple(y) > snake(y)
        if self.apple_pos[1] > self.snake_segments[0][1]:
            apple_below = 1 

        # Left of
        if self.apple_pos[0] < self.snake_segments[0][0]:
            apple_left = 1 

        return apple_above, apple_right, apple_below, apple_left

    # Calculate scalar distance between snake head's and apple
    def _distance_to_apple(self, snake=None):
        if not snake:
            snake = self.snake_segments[0] # snake's head

        snake_x = snake[0]
        snake_y = snake[1]        
        apple_x = self.apple_pos[0]
        apple_y = self.apple_pos[1]


        # Calculate distance formula
        max_distance = math.sqrt(self.ENV_WIDTH**2 + self.ENV_HEIGHT**2)
        distance = math.sqrt((apple_x - snake_x)**2 + (apple_y - snake_y)**2)

        # Normalized distance
        norm_distance = 1- (distance / max_distance) # Higher value for closer distance (increase neuron stimulation?)

        return norm_distance
    '''