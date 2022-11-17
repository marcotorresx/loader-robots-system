from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agent import RandomAgent, ObstacleAgent, DestinyAgent, BoxAgent

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        N: Number of agents in the simulation
        height, width: The size of the grid to model
    """
    def __init__(self, N, width, height, timer):
        self.num_agents = N
        self.grid = MultiGrid(width, height, torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True 
        self.timer = timer
        self.count = 0

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        # Place the obstacle agents
        for i in range(len(border)):
            obs = ObstacleAgent(i+4000, self)
            self.grid.place_agent(obs, border[i])

        # Place the destiny agents
        destiny_positions = [(1,1), (8,1), (1,8), (8,8)]
        for i in range(4):
            dest = DestinyAgent(i+3000, self) 
            self.grid.place_agent(dest, destiny_positions[i])

        # Place the box agents
        for i in range(20):
            box = BoxAgent(i+2000, self) 

            # Obtain one random potition of the grid to place the trash agent
            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)

            # Find an empty cell to place the trash  
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)

            self.grid.place_agent(box, pos)

        # Place
        for i in range(5):
            agent = RandomAgent(i+1000, self) 
            self.schedule.add(agent)

            # Obtain one random potition of the grid to place the trash agent
            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)

            # Find an empty cell to place the trash  
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)

            self.grid.place_agent(agent, pos)


    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()
        