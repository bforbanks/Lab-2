# Game 2048: Artificial intelligence

# Instructions:
#   Move up, down, left, or right to merge the tiles. The objective is to 
#   get a tile with the number 2048 (or higher)
#
# Control:
#    arrows  : Merge up, down, left, or right
#    r       : Restart game
#    q / ESC : Quit

from Game2048 import Game2048
import numpy as np
import pygame
import random
import time


class SimGame2048:

    scores = []

    def __init__(self, first_step, current_board, current_score):
        self.first_step = first_step
        self.current_board = current_board
        self.current_score = current_score

    def run(self):
        print("start")
        sim = Game2048((self.current_board, self.current_score))

        for i in range(100):
            sim.reset()
            (board, score), reward, done = sim.step(self.first_step)
            done = False
            while not done:                
                action = actions[np.random.randint(4)]
                (board, score), reward, done = sim.step(action)
            
            self.scores.append(score)
        return sum(self.scores)/len(self.scores)
        # while not done:                

env = Game2048()
env.reset()
actions = ['left', 'up', 'down', 'right']
exit_program = False
action_taken = False
lastGameState = []
board = []

while not exit_program:
    env.render()

    sim_results = {}

    for direction in actions:
        sim = SimGame2048(direction, env.board, env.score)
        sim_results.update({sim.run() : direction})

    print(sim_results)
    #TODO: fix this
    direction_to_go = sim_results[sorted(sim_results[0])]

    print(direction_to_go)

    time.sleep(3)


    action, action_taken  = random.choice(actions), True

    if action_taken:
        (board, score), reward, done = env.step(action)
        action_taken = False



    # Process game events
    # for event in pygame.event.get():
    #     if event.type == pygame.QUIT:
    #         exit_program = True
    #     if event.type == pygame.KEYDOWN:
    #         if event.key in [pygame.K_ESCAPE, pygame.K_q]:
    #             exit_program = True
    #         if event.key == pygame.K_UP:
    #             action, action_taken = 'up', True
    #         if event.key == pygame.K_DOWN:
    #             action, action_taken  = 'down', True
    #         if event.key == pygame.K_RIGHT:
    #             action, action_taken  = 'right', True
    #         if event.key == pygame.K_LEFT:
    #             action, action_taken  = 'left', True
    #         if event.key == pygame.K_r:
    #             env.reset()    
env.close()

