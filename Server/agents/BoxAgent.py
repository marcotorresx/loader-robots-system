from mesa import Agent

class BoxAgent(Agent):
    """
    Box agent. Just to add box to the grid.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def step(self):
        pass