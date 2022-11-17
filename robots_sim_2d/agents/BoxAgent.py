from mesa import Agent

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