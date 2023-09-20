
from concurrent.futures import ProcessPoolExecutor
from functools import partial
from concurrent.futures import wait

class SimGame2048:
    scores = []

    def __init__(self, first_step, current_board, initial_score):
        self.first_step = first_step
        self.initial_board = current_board
        self.initial_score = initial_score
        self.initial_board_score = self.calculate_board_score(current_board)

    def calculate_board_score(self, board):
        board_score = 0
        for tile in np.concatenate(board):
            if tile == 0:
                board_score = board_score + 1
        return board_score

    def run(self):
        actions = ['left', 'up', 'down', 'right']
        from Game2048 import Game2048
        import numpy as np
        sim = Game2048((self.initial_board, self.initial_score))
        if(not sim.move_is_legal(self.first_step)):
            return 0
        for i in range(100):
            sim.set_state((self.initial_board, self.initial_score))
            (board, score), reward, done = sim.step(self.first_step)
            done = False
            current_depth = 0
            max_depth = 5
            alive = 1
            while not done and current_depth < 5:                
                action = actions[np.random.randint(4)]
                (board, score), reward, done = sim.step(action)
                current_depth += 1
            if(current_depth < max_depth):
                alive = 0


            board_score = self.calculate_board_score(board)

            self.scores.append(board_score + (1 + score)*10/(1 + self.initial_score))
        return sum(self.scores)/len(self.scores)


def sim_factory(direction, board, score):
    from AI_Game2048 import SimGame2048
    sim = SimGame2048(direction, board, score)
    return {sim.run() : direction}

def main():
    env = Game2048()
    env.reset()
    actions = ['left', 'up', 'down', 'right']
    exit_program = False
    action_taken = False
    lastGameState = []
    board = []

    executor = ProcessPoolExecutor(4)

    while not exit_program:
        env.render()

        sim_results = {}

        ## this is the function that will run in it's own process. It will start the sim, and retun the result to the main thread.

        # this will start 4 process, that will calculate the different directions
        futures = [executor.submit(sim_factory, direction=direction, board=env.board, score=env.score) for direction in actions]
        wait(futures)
        for result in futures:
            sim_results.update(result.result())
        print(sim_results)
        direction_to_go = sim_results[sorted(sim_results)[-1]]


        action, action_taken  = direction_to_go, True

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

if __name__ ==  '__main__':
    from Game2048 import Game2048
    import numpy as np
    main()