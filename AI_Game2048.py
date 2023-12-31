from concurrent.futures import ProcessPoolExecutor
from concurrent.futures import wait
import numpy as np  
class SimGame2048ForOneDirection:
    """
    This is a class for the one of the directions. All the variable will be set in the constructor,
    And then the run method, will run the actuall simulations
    Important settings just below
    """

    # This is the simulationcount for each process. If you only have the first line 
    # active it will be this value simulations pr. direction. 
    # If you have 2 lines active = 2*simulation_count for each direction
    simulation_count = 200
    scores=[]

    def __init__(self, first_step, current_board, initial_score,max_depth):
        self.first_step = first_step
        self.initial_board = current_board
        self.initial_score = initial_score
        self.max_depth=max_depth

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
            return [-1]
        
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
            if(current_depth < self.max_depth):
                self.scores.append(0)
                continue

            self.scores.append(score)


        return self.scores


def sim_factory(direction, board, score, max_depth):
    """
    A function to run in its own process, and be a wrapper around the simulation for one direction.
                futures.append(process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions)

    It will start the simulation, and retun the result to the main thread.

    Args:
        board(board): The initial board-state for all the simulations
        score(int): The initial score of the board for all the simulations
    """
    from AI_Game2048 import SimGame2048ForOneDirection
    sim = SimGame2048ForOneDirection(direction, board, score, max_depth)
    return {'direction': direction, 'score': sim.run()}

def main():
    """
    The main function. Only to be run on the main thread.
    """
    actions = ['left', 'up', 'down', 'right']
    exit_program = False
    process_pool = ProcessPoolExecutor(16)

    # here you can change MSD. It is a range so it will start with the first MSD, and will continue to 
    # loop over that one MSD until the confidence interval 95%
    for max_simulation_depth in range(4,11):
        if exit_program:
            break

        # initalization of the stastistical feedback system
        scores = []
        confidence_interval=0
        mean=0

        # loop the games for a specific max_simulation_depth
        while (confidence_interval>=0.05*mean or len(scores)<30) and not exit_program:

            env = Game2048()
            env.reset()

            action_taken = False
            done = False

            # loop the steps of a game
            while not done and not exit_program:

                # comment out this line, if you want to stop the rendering
                env.render()

                # this will start 4 process, that will calculate the different directions. 
                # a future is a representation of the function call to the process.
                # this represents. This first line is the first processes for each direction
                futures = [process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score, max_depth=max_simulation_depth) for direction in actions]

                # each of these lines adds another process for each direction. So one line adds 4 extra processes:
                futures.extend([process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score, max_depth=max_simulation_depth) for direction in actions])
                # futures.extend([process_pool.submit(sim_factory, direction=direction, board=env.board, score=env.score, max_depth=max_depth) for direction in actions])

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

                # process game events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        process_pool.shutdown()
                        exit_program = True
                        break
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                        env.reset()
                        for future in futures:
                            future.cancel()

            # after each game use the stastistical feedback system to calculate the confidence_interval
            scores.append(score)
            mean = sum(scores)/len(scores)
            sd = np.sqrt(sum([(s-mean)**2 for s in scores])/(len(scores)-1))
            confidence_interval = 1.96*sd/np.sqrt(len(scores))

            print(score, " ; ", confidence_interval, "/", 0.05*mean)

        print(f'Max Depth: {max_simulation_depth}; Mean: {mean}, Confidence Interval: {mean - confidence_interval} - {confidence_interval + mean}')
        with open(r"./results simcount=400","a") as f:
            f.write((f'Max Depth: {max_simulation_depth}; Mean: {mean}; Confidence Interval: {mean - confidence_interval} - {confidence_interval + mean}; Raw: {scores}\n'))
       
    env.close()
    exit()

if __name__ ==  '__main__':
    from Game2048 import Game2048
    import numpy as np
    import pygame
    main()