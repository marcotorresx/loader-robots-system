from mesa import Agent
# import math
from math import sqrt

class RandomAgent(Agent):
    """
    Agent that moves randomly.
    Attributes:
        unique_id: Agent's ID 
        direction: Randomly chosen direction chosen from one of eight directions
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
        self.nearestPoint = None

    def step(self):
        """ 
        Determines the new direction it will take, and then moves
        """
        # self.direction = self.random.randint(0,8)
        # print(f"Agente: {self.unique_id} movimiento {self.direction}")

        isBoxInMyCell = self.get_box_in_my_cell()

        if self.box:
            self.moveWithBox()

        elif isBoxInMyCell:
            self.box = isBoxInMyCell
            self.nearestPoint = self.getNearestPoint()
            
        else: 
            self.move()

    

    def move(self):
     
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=False, 
            include_center=True
        ) 
   
        # Check for empty spaces and spaces with box
        freeSpaces = self.move_free_spaces(possible_steps)
        boxSpaces = self.move_box_spaces(possible_steps)
        
        # The agents will choose move to cells with box instead empty cells
        next_moves = [p for p,f in zip(possible_steps, boxSpaces) if f == True]
        
        # If there is no box near, the next moves will take empty spaces
        if(len(next_moves) == 0):
            next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]

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
        if(self.nearestPoint in possible_steps):
            next_moves.append(self.nearestPoint)
        else:
            # Check for empty spaces and spaces with box
            freeSpaces = self.move_free_spaces(possible_steps)
            # The agents will choose move to cells with box instead empty cells
            next_moves = [p for p,f in zip(possible_steps, freeSpaces) if f == True]

        # Check if the agent can move arround itself, if can not move
        # the agent will wait until exist free spaces
        if len(next_moves) > 0:
            furthestDistance = 1000000000
            next_move = None
            # eliminate the cell that drives you the furthes to the nearest point
            if len(next_moves) > 1:
                for i in range(len(next_moves)):
                    distance = self.getDistance(next_moves[i], self.nearestPoint)
                    if(distance < furthestDistance):
                        next_move = next_moves[i]
                        furthestDistance = distance
                # for i in range(len(next_moves)):
                #     if(next_moves[i] == next_move):
                #         next_moves.pop(i) 

            # choose the next move randmly between the new possible moves
            # next_move = self.random.choice(next_moves)
            if (next_move == None):
                next_move = next_moves[0]
            self.model.grid.move_agent(self, next_move) 
            self.box.model.grid.move_agent(self.box, next_move)
            self.steps_taken+=1
                    


    def getDistance(self, point1, point2):
        """
        Function obtain the distance between two points
        """
        distX = point1[0] - point2[0]
        distY = point1[1] - point2[1]
        dist = sqrt(distX**2 + distY**2)
        return dist


    def getNearestPoint(self):
        """
        Function obtain the nearest point to the agent
        """
        points = [(1,1), (1,8), (8,1), (8,8)]
        minDistance = 0
        nearestPoint = None
        
        # Get distances with pythagoras
        for i in range(4):
            point = points[i]
            distX = point[0] - self.pos[0]
            distY = point[1] - self.pos[1]
            dist = sqrt(distX**2 + distY**2)
            if minDistance > dist or minDistance == 0:
                minDistance = dist
                nearestPoint = point
                
        return nearestPoint



    def get_box_in_my_cell(self):
        '''Regresar si hay unq caja en mi celda'''

        # Obtener todas las celdas de mi alrededor y de mi celda
        neighbors = self.model.grid.get_neighbors(
            self.pos,
            moore=False, 
            include_center=True
        ) 
        
        # Buscar en mi celda actual 
        for n in neighbors:
            # Si el agente vecino está en mi celda y es basura
            if n.pos == self.pos and isinstance(n, BoxAgent):
                return n

        return None
        


    def move_free_spaces(self, possible_steps):
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

    def move_box_spaces(self, possible_steps):
        """
        Function obtain the spaces which contain box
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
                        for agent in contents:
                            if isinstance(agent, BoxAgent):
                                freeSpaces.append(True)
                            else:
                                freeSpaces.append(False)
        return freeSpaces




class ObstacleAgent(Agent):
    """
    Obstacle agent. Just to add obstacles to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass  



class DestinyAgent(Agent):
    """
    Destiny agent. Just to add destiny to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.amountOfBoxes = 0

    def step(self):
        pass

    def addBox(self):
        self.amountOfBoxes += 1



class BoxAgent(Agent):
    """
    Box agent. Just to add box to the grid.
    """
    PENDING_MOVEMENT = 0 
    MOVING = 1
    IN_PLACE = 2
    
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.isTaken = False
        self.isOrdered = False
        self.status = self.PENDING_MOVEMENT

    def step(self):
        pass

    def move(self, cell):
        if self.status == self.MOVING:
            self.model.grid.move_agent(self, cell)
