from model import RandomModel, ObstacleAgent, BoxAgent, DestinyAgent
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter

def agent_portrayal(agent):
    if agent is None: return
    
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.5}

    if (isinstance(agent, ObstacleAgent)):
        portrayal["Color"] = "grey"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.3

    if (isinstance(agent, BoxAgent)):
        portrayal["Color"] = "brown"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.2 

    if (isinstance(agent, DestinyAgent)):
        portrayal["Color"] = "green"
        portrayal["Layer"] = 1
        portrayal["r"] = 0.7 

    return portrayal

grid = CanvasGrid(agent_portrayal, 15, 15, 500, 500)

model_params = {
    "num_agents": UserSettableParameter("slider", "Number of Robots", 1, 1, 10, 1), 
    "width": 15, 
    "height": 15, 
    "boxes": 20
}

server = ModularServer(RandomModel, [grid], "Loader Robots", model_params)
                       
server.port = 8521 # The default
server.launch()