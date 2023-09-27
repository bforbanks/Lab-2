
from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
import numpy as np  
from functools import reduce
   

class SimGame2048:
    """
    Important settings just below
    """
    max_depth = 5
    # This is the simulationcount for each process. If you only have the first line 
    # active it will be this value simulations pr. direction. 
    # If you have 2 lines active = 2*simulation_count for each direction
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
        self.scores=[]


        if(not sim.move_is_legal(self.first_step)):
            return [0]
        
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

            # self.scores.append(board_score + (1 + score)*10/(1 + self.initial_score))
            if(self.initial_score != 0):
                self.scores.append(np.floor(score-self.initial_score))
            else:
                self.scores.append(score)


        return self.scores


def sim_factory(direction, board, score):
    """
    A function to run in its own process, and be a wrapper around the simulation for one direction.
                futures.append(process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions)

    It will start the simulation, and retun the result to the main thread.

    Args:
        board(board): The initial board-state for all the simulations
        score(int): The initial score of the board for all the simulations
    """
    from AI_Game2048 import SimGame2048
    sim = SimGame2048(direction, board, score)
    return {'direction': direction, 'score': sim.run()}

def main():
    """
    The main function. Only to be run on the main thread.
    """
    actions = ['left', 'up', 'down', 'right']
    exit_program = False
    process_pool = ProcessPoolExecutor(16)

    while not exit_program:
        scores = []
        confidence_interval=0
        mean=0
        ## The entire stat loop
        while confidence_interval>=0.05*mean or len(scores)<30:

            env = Game2048()
            env.reset()

            action_taken = False
            done = False

            ## One game, loop the steps
            while not done and not exit_program:
                env.render()

                # this will start 4 process, that will calculate the different directions. 
                # a future is a representation of the function call to the process.
                # this represents. This first line is the first processes for each direction
                futures = [process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions]
                # each of these lines adds another process for each direction. So one line adds 4 extra processes:
                futures.extend([process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions])
                futures.extend([process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions])

                # wait for all the process-calls to be done
                wait(futures)
                results = []
                total_directions = []

                for future in futures:
                    results.append(future.result())

                for direction in actions:
                    direction_result = map(lambda x: x['score'], list(filter(lambda r: r['direction'] == direction, results)))
                    direction_results = []
                    for r in direction_result:
                        direction_results.extend(r)
                    total_directions.append({'direction': direction, 'score_sum': sum(direction_results)/len(direction_results)})     

                direction_to_go = sorted(total_directions, key=lambda d: d['score_sum'])[-1]['direction']
                action, action_taken  = direction_to_go, True

                if action_taken:
                    (board, score), reward, done = env.step(action)
                    action_taken = False

                # Process game events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        process_pool.shutdown()
                        exit_program = True
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        env.reset()
                        for future in futures:
                            future.cancel()

            # Stat stuff
            scores.append(score)
            mean = sum(scores)/len(scores)
            sd = np.sqrt(sum([(s-mean)**2 for s in scores])/(len(scores)-1))
            confidence_interval = 1.96*sd/np.sqrt(len(scores))
            print(score, " > ", confidence_interval)
        print(f'Mean: {mean}, Confidence Interval: {mean - confidence_interval} - {confidence_interval + mean}')

        

    env.close()

if __name__ ==  '__main__':
    from Game2048 import Game2048
    import numpy as np
    import pygame
    main()