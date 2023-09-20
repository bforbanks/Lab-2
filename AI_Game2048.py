
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from concurrent.futures import wait

class SimGame2048:
    """
    Important settings just below
    """
    max_depth = 5
    simulation_count = 100

    scores = []

    def __init__(self, first_step, current_board, initial_score):
        self.first_step = first_step
        self.initial_board = current_board
        self.initial_score = initial_score
        self.initial_board_score = self.calculate_empty_cells(current_board)

    def calculate_empty_cells(self, board):
        """
        Args: 
            board (board): The board to check

        Returns:
            int: Number of empty cells
        """
        board_score = 0
        import numpy as np
        for tile in np.concatenate(board):
            if tile == 0:
                board_score = board_score + 1
        return board_score

    def run(self):
        """
        Runs multiple simulations, by using the first move from the constructor.
        
        Returns:
            float: The average score of the simulations
        """
        from Game2048 import Game2048
        import numpy as np


        actions = ['left', 'up', 'down', 'right']
        sim = Game2048((self.initial_board, self.initial_score))

        if(not sim.move_is_legal(self.first_step)):
            return 0
        
        # loop for running n simulations
        for i in range(self.simulation_count):

            sim.set_state((self.initial_board, self.initial_score))
            (board, score), reward, done = sim.step(self.first_step)

            done = False
            current_depth = 0

            # loop for each step of a simulation
            while not done and current_depth < self.max_depth:                
                action = actions[np.random.randint(4)]
                (board, score), reward, done = sim.step(action)
                current_depth += 1
                # TODO: maybe implement scoring system that gives points
                #  based on the current state for each step

            # if game_over
            # TODO: check if the game have been won and give a lot of points
            if(current_depth < self.max_depth):
                self.scores.append(0)
                continue

            # the scoring function if stil alive
            board_score = self.calculate_empty_cells(board)
            self.scores.append(board_score + (1 + score)*10/(1 + self.initial_score))

        return sum(self.scores)/len(self.scores)


def sim_factory(direction, board, score):
    """
    A function to run in its own process, and be a wrapper around the simulation for one direction.
    It will start the simulation, and retun the result to the main thread.

    Args:
        board(board): The initial board-state for all the simulations
        score(int): The initial score of the board for all the simulations
    """
    from AI_Game2048 import SimGame2048
    sim = SimGame2048(direction, board, score)
    return {sim.run() : direction}

def main():
    """
    The main function. Only to be run on the main thread.
    """
    env = Game2048()
    env.reset()
    actions = ['left', 'up', 'down', 'right']
    exit_program = False
    action_taken = False
    process_pool = ProcessPoolExecutor(4)

    while not exit_program:
        env.render()

        sim_results = {}


        # this will start 4 process, that will calculate the different directions. 
        # a future is a representation of the function call to the process.
        # TODO: maybe add multiple processes for each direaction
        futures = [process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions]

        # wait for all the process-calls to be done
        wait(futures)

        # extract the results of the simulations from the thread futures
        for future in futures:
            sim_results.update(future.result())
        print(sim_results)

        direction_to_go = sim_results[sorted(sim_results)[-1]]
        action, action_taken  = direction_to_go, True

        if action_taken:
            (board, score), reward, done = env.step(action)
            action_taken = False

        # Process game events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                process_pool.shutdown()
                exit_program = True
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    exit_program = True
                if event.key == pygame.K_UP:
                    action, action_taken = 'up', True
                if event.key == pygame.K_DOWN:
                    action, action_taken  = 'down', True
                if event.key == pygame.K_RIGHT:
                    action, action_taken  = 'right', True
                if event.key == pygame.K_LEFT:
                    action, action_taken  = 'left', True
                if event.key == pygame.K_r:
                    env.reset()
                    for future in futures:
                        future.cancel()

    env.close()

if __name__ ==  '__main__':
    from Game2048 import Game2048
    import numpy as np
    import pygame
    main()