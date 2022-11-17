from mesa import Agent

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