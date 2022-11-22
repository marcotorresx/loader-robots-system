from mesa import Model, agent
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from agents.RandomAgent import RandomAgent
from agents.ObstacleAgent import ObstacleAgent
from agents.DestinyAgent import DestinyAgent
from agents.BoxAgent import BoxAgent

class RandomModel(Model):
    """ 
    Creates a new model with random agents.
    Args:
        num_agents: Number of agents in the simulation
        height, width: The size of the grid to model
        boxes: Number of boxes
    """
    def __init__(self, num_agents, width, height, boxes):
        self.num_agents = num_agents
        self.height = height
        self.width = width
        self.boxes = boxes
        self.collected_boxes = 0
        self.grid = MultiGrid(width, height, torus = False) 
        self.schedule = RandomActivation(self)
        self.running = True
        self.visited_cells = set()
        self.destinations = [] # Destiny agents of the grid (object reference)
        self.destiny_points = [
            (1, 1), 
            (1, self.height - 2), 
            (self.width - 2, 1), 
            (self.width - 2, self.height - 2)
        ] # Destinations coordinates 

        # Creates the border of the grid
        border = [(x,y) for y in range(height) for x in range(width) if y in [0, height-1] or x in [0, width - 1]]

        # Place the obstacle agents
        for i in range(len(border)):
            obs = ObstacleAgent(i+4000, self)
            self.grid.place_agent(obs, border[i]) # Place obstacle in grid

        # Place the destiny agents 
        for i in range(4):
            dest = DestinyAgent(i+3000, self) 
            self.destinations.append(dest) # Add destiny object to the destinations of the model
            self.schedule.add(dest)
            self.grid.place_agent(dest, self.destiny_points[i]) # Place destination in grid

        # Place the box agents
        for i in range(self.boxes):
            box = BoxAgent(i+2000, self) 

            # Obtain one random potition of the grid to place the box agent
            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)

            # Find an empty cell to place the trash  
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)

            self.grid.place_agent(box, pos)

        # Place the robot agents
        for i in range(self.num_agents):
            agent = RandomAgent(i+1000, self) 
            self.schedule.add(agent)

            # Obtain one random potition of the grid to place the robot agent
            pos_gen = lambda w, h: (self.random.randrange(w), self.random.randrange(h))
            pos = pos_gen(self.grid.width, self.grid.height)

            # Find an empty cell to place the trash  
            while (not self.grid.is_cell_empty(pos)):
                pos = pos_gen(self.grid.width, self.grid.height)

            self.grid.place_agent(agent, pos)



    def step(self):
        '''Advance the model by one step.'''
        self.schedule.step()

        # End program when all boxes are collected
        if self.collected_boxes >= self.boxes:
            self.running = False
        