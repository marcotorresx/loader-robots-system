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

grid = CanvasGrid(agent_portrayal, 10, 10, 500, 500)

model_params = {
    "N": UserSettableParameter("slider", "Number of roombas", 1, 1, 10, 1), 
    "width": 10, 
    "height": 10, 
    "timer": UserSettableParameter("slider", "Timer", 10, 10, 100, 5)
}

server = ModularServer(RandomModel, [grid], "Loader Robots", model_params)
                       
server.port = 8521 # The default
server.launch()