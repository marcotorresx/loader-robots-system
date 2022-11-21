from mesa import Agent
from .BoxAgent import BoxAgent
from .DestinyAgent import DestinyAgent
from math import sqrt

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of four directions
    """


    def __init__(self, unique_id, model):
        """
        Creates a new random agent.
        Args:
            unique_id: The agent's ID
            model: Model reference for the agent
        """
        super().__init__(unique_id, model)
        self.steps_taken = 0
        self.steps_to_destiny = 0 # Counter of the taken steps to the current destiny
        self.limit_steps_to_destiny = self.model.width # Limit of steps in wich the agent should change destiny
        self.box = None # Will be the picked up box object reference
        self.nearest_destiny = None # Will be the object reference to the destiny agent


    def step(self):
        """Decides wich is the procedure that the robot needs to make"""

        # If the robot already is carrying a box
        if self.box:
            
            # If the nearest destiny its blocked the robot could be trapped in a loop, so we put a limit
            # of steps in which a robot can get to the destiny (the limit is the width of the grid). If
            # the robot reaches the limit, it will change of destiny because its probably traped

            # Check if the limit of steps to a destiny has been reached or the destiny is already full
            if self.steps_to_destiny >= self.limit_steps_to_destiny or self.nearest_destiny.full:
                self.change_destiny()

            # Move to destiny with box
            self.move_with_box()
            return

        # Check if there is a new box in my current cell
        is_box_in_my_cell = self.get_box_in_my_cell()

        # If the robot wasn´t carrying a box and if it had found a new box
        if is_box_in_my_cell:
            self.box = is_box_in_my_cell # Set new box
            self.box.is_taken = True
            self.nearest_destiny = self.get_nearest_destiny() # Set new destiny
            return
         
        # Move to find a box
        self.move()


    def move(self):
        """ Move agent to search boxes"""

        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, 
            include_center=False
        ) 
   
        # Check for empty cells and cells with a box
        empty_cells = self.get_empty_cells(possible_steps)
        box_cells = self.get_box_cells(possible_steps)

        # The agents will choose move to cells with box instead empty cells
        next_moves = [p for p, f in zip(possible_steps, box_cells) if f == True]
        
        # If there is no box near, the next moves will take empty spaces
        if len(next_moves) == 0:
            next_moves = [p for p,f in zip(possible_steps, empty_cells) if f == True]

        # Check if the agent has any cell to move, if not it will stay in its position
        if len(next_moves) > 0:
            # Prefer to go to an unvisited cell
            next_move = None
            for move in next_moves:
                if not move in self.model.visited_cells:
                    next_move = move
                    break
            
            # If all neighbor cells are already visited
            if not next_move:
                next_move = self.random.choice(next_moves) # Choose a random movment

            self.model.grid.move_agent(self, next_move)
            self.model.visited_cells.add(next_move) # Add cell to visited cells
            self.steps_taken += 1


    def move_with_box(self):
        """Moves to destiny with the box"""

        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, 
            include_center=False
        )

        next_moves = []

        # If destiny is my possible steps set it as next moves
        if self.nearest_destiny.pos in possible_steps:
            next_moves.append(self.nearest_destiny.pos)

        else:
            # Check for empty spaces and spaces with box
            empty_cells = self.get_empty_cells(possible_steps)
            # The next moves are going to be empty cells
            next_moves = [p for p, f in zip(possible_steps, empty_cells) if f == True]

        # Check if the agent has any cell to move, if not it will stay in its position
        if len(next_moves) > 0:

            # Get the next move that has the smallest distance
            next_move = None
            min_distance = 1000000000
            if len(next_moves) > 1:
                for i in range(len(next_moves)):
                    # Get the distance from cur next move to destiny
                    distance = self.get_distance(next_moves[i], self.nearest_destiny.pos)
                    # Check if its new min
                    if distance < min_distance:
                        next_move = next_moves[i]
                        min_distance = distance

            # If agent is next to destiny
            if next_move == None and (next_moves[0] in self.model.destiny_points):
                self.leave_box(next_moves[0]) # Leave box in destiny             

            else:
                self.model.grid.move_agent(self, next_move or next_moves[0]) # Move agent
                self.box.model.grid.move_agent(self.box, next_move or next_moves[0]) # Move box to the same cell
                self.model.visited_cells.add(next_move or next_moves[0]) # Add to visited cells
                self.steps_taken += 1
                self.steps_to_destiny += 1 # Increase steps to destiny
                    

    def get_distance(self, point1, point2):
        """Function obtain the distance between two points"""
        dist_x = point1[0] - point2[0]
        dist_y = point1[1] - point2[1]
        dist = sqrt(dist_x**2 + dist_y**2)
        return dist


    def get_nearest_destiny(self):
        """Function that obtains the nearest destiny point"""

        destinations = self.model.destinations
        min_distance = 0
        nearest_destiny = None
        
        # Get distances with pythagoras
        for i in range(len(destinations)):
            point = destinations[i].pos

            # Get distance from agent to point in x and y axes
            dist_x = point[0] - self.pos[0]
            dist_y = point[1] - self.pos[1]

            # Obtain distance with pythagoras
            dist = sqrt(dist_x**2 + dist_y**2)

            # Check if its nearest
            if min_distance > dist or min_distance == 0:
                min_distance = dist
                nearest_destiny = destinations[i]
                
        return nearest_destiny


    def get_box_in_my_cell(self):
        '''If there is a box in my cell, returns the box, if not return None'''

        # Get neighbor cells to access my cell
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=False, 
            include_center=True
        ) 
        
        # Search in my current cell
        for n in neighbors:
            # If the there is a box agent in my cell
            if n.pos == self.pos and isinstance(n, BoxAgent):
                return n # Return box

        return None
        

    def get_empty_cells(self, possible_steps):
        """Function obtain the free spaces of the possible steps"""

        empty_spaces = []
        for i in range(len(possible_steps)):
            # Get the content and iterate each cell of the grid
            for (contents, w, h) in self.model.grid.coord_iter():
                # If the cell is a possible step
                if (w, h) == possible_steps[i]:
                    # Check if it has 0 agents
                    if len(contents) == 0:
                        empty_spaces.append(True)
                    else: 
                        empty_spaces.append(False)

        return empty_spaces


    def get_box_cells(self, possible_steps):
        """Function that obtains the cells which contain a box"""

        box_cells = []
        for i in range(len(possible_steps)):
            # Get the content and iterate each cell of the grid
            for (contents, w, h) in self.model.grid.coord_iter():
                # If the cell is a possible step
                if (w, h) == possible_steps[i]:
                    # If the cell is empty, there is not a box
                    if len(contents) == 0:
                        box_cells.append(False)
                    # If there are more than 1 agent, the box is already in a destiny, so ignore it
                    elif len(contents) > 1:
                        box_cells.append(False)
                    # Check if agent is a box
                    else:
                        box_founded = False
                        for agent in contents:
                            if isinstance(agent, BoxAgent):
                                box_founded = True
                        box_cells.append(box_founded)
                        
        return box_cells


    def change_destiny(self):
        """Function that changes the nearest destiny of the agent"""

        for destiny in self.model.destinations:
            # Find a different destiny
            if destiny != self.nearest_destiny:
                self.nearest_destiny = destiny # Set new destiny
                self.steps_to_destiny = 0 # Reset steps to destiny
                return

        # Note: When a destiny agent is full, it is removed from the model.destinations array,  
        # so in the selection of a new destiny, we are making sure the new one its not already full


    def leave_box(self, next_move):
        """Set all the variables involved with the leaving of a box in a destiny"""
        self.box.model.grid.move_agent(self.box, next_move) # Move box to destiny
        self.box.is_taken = False
        self.box.order = self.nearest_destiny.amount_of_boxes * 0.35
        self.nearest_destiny.add_box() # Increase destiny box counter
        self.steps_to_destiny = 0
        self.box = None
        self.nearest_destiny = None
        self.steps_taken += 1
        self.model.collected_boxes += 1