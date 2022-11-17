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
        self.direction = 4
        self.steps_taken = 0
        self.box = None
        self.nearest_destiny = None
        self.points = [(1,1), (1,8), (8,1), (8,8)]


    def step(self):
        """ 
        Decides wich is the procedure that the robot needs to make
        """

        # Check if there is a box in my current cell
        is_box_in_my_cell = self.get_box_in_my_cell()

        # If the robot already is carrying a box
        if self.box:
            # Move to destiny with box
            self.moveWithBox() 

        # If not, if it had found a new box
        elif is_box_in_my_cell:
            self.box = is_box_in_my_cell
            self.nearest_destiny = self.get_nearest_destiny()
        
        # If not, continue searching boxes
        else: 
            # Move to find a box
            self.move()


    def move(self):
        """ 
        Move agent to search for boxes
        """
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, 
            include_center=True
        ) 
   
        # Check for empty cells and cells with a box
        empty_cells = self.get_empty_cells(possible_steps)
        box_cells = self.get_box_cells(possible_steps)

        print(possible_steps)
        print("E")
        print(empty_cells)
        print("B")
        print(box_cells)

        # The agents will choose move to cells with box instead empty cells
        next_moves = [p for p,f in zip(possible_steps, box_cells) if f == True]
        
        # If there is no box near, the next moves will take empty spaces
        if(len(next_moves) == 0):
            next_moves = [p for p,f in zip(possible_steps, empty_cells) if f == True]

        # Check if the agent can move arround itself, if can not move
        # the agent will wait until exist free spaces
        if len(next_moves) > 0:
            next_move = self.random.choice(next_moves) 
            
            self.model.grid.move_agent(self, next_move) 
            self.steps_taken+=1


    def moveWithBox(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, 
            include_center=True
        )
        next_moves = []
        if(self.nearest_destiny in possible_steps):
            next_moves.append(self.nearest_destiny)
        else:
            # Check for empty spaces and spaces with box
            empty_cells = self.get_empty_cells(possible_steps)
            # The agents will choose move to cells with box instead empty cells
            next_moves = [p for p,f in zip(possible_steps, empty_cells) if f == True]

        # Check if the agent can move arround itself, if can not move
        # the agent will wait until exist free spaces
        if len(next_moves) > 0:
            furthestDistance = 1000000000
            next_move = None
            # eliminate the cell that drives you the furthes to the nearest point
            if len(next_moves) > 1:
                for i in range(len(next_moves)):
                    distance = self.getDistance(next_moves[i], self.nearest_destiny)
                    if(distance < furthestDistance):
                        next_move = next_moves[i]
                        furthestDistance = distance

            if (next_move == None and (next_moves[0] in self.points)):

                next_move = next_moves[0]
                self.box.model.grid.move_agent(self.box, next_move)
                self.box.isTaken = False
                self.box.isOrdered = True
                self.deleteBox()
                self.box = None
                self.nearest_destiny = None
                self.steps_taken+=1

            else:
                self.model.grid.move_agent(self, next_move or next_moves[0])
                self.box.model.grid.move_agent(self.box, next_move or next_moves[0])
                self.steps_taken+=1
                    

    def getDistance(self, point1, point2):
        """
        Function obtain the distance between two points
        """
        distX = point1[0] - point2[0]
        distY = point1[1] - point2[1]
        dist = sqrt(distX**2 + distY**2)
        return dist


    def get_nearest_destiny(self):
        """
        Function that obtains the nearest destiny point
        """
        points = self.model.destiny_points
        min_distance = 0
        nearest_destiny = None
        
        # Get distances with pythagoras
        for i in range(len(points)):
            point = points[i]

            # Get distance from agent to point in x and y axes
            dist_x = point[0] - self.pos[0]
            dist_y = point[1] - self.pos[1]

            # Obtain distance with pythagoras
            dist = sqrt(dist_x**2 + dist_y**2)

            # Check if its nearest
            if min_distance > dist or min_distance == 0:
                min_distance = dist
                nearest_destiny = point
                
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
        """
        Function obtain the free spaces of the possible steps
        """
        freeSpaces = []
        for i in range(len(possible_steps)):
            for (contents, w, h) in self.model.grid.coord_iter():
                if (w, h) == possible_steps[i]:
                    if(len(contents) == 0):
                        freeSpaces.append(True)
                        pass

                    elif(len(contents) > 1):   
                        freeSpaces.append(False)
                    else: 
                        freeSpaces.append(False)
        return freeSpaces


    def get_box_cells(self, possible_steps):
        """
        Function that obtains the cells which contain a box
        """
        freeSpaces = []
        for i in range(len(possible_steps)):
            for (contents, w, h) in self.model.grid.coord_iter():
                if (w, h) == possible_steps[i]:
                    if(len(contents) == 0):
                        freeSpaces.append(False)
                        pass

                    elif(len(contents) > 1):

                        freeSpaces.append(False)
                    else:
                        counter = 0
                        for agent in contents:
                            if isinstance(agent, BoxAgent):
                                counter+=1
                                freeSpaces.append(True)
                        if counter == 0:
                            freeSpaces.append(False)
        return freeSpaces


    def deleteBox(self):
        """
        Function delete the box from the list of boxes
        """
        for (contents, w, h) in self.model.grid.coord_iter():
            if(self.nearest_destiny == (w, h)):
                for agent in contents:
                    if isinstance(agent, DestinyAgent):
                        agent.addBox()