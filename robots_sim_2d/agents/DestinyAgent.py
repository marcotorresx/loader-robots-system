from mesa import Agent

class DestinyAgent(Agent):
    """
    Destiny agent. Just to add destiny to the grid.
    """
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.amount_of_boxes = 0
        self.full = False

    def step(self):

        if self.amount_of_boxes >= 5:
            self.full = True
            self.model.destinations = [item for item in self.model.destinations if not item.full]


    def addBox(self):
        self.amount_of_boxes += 1