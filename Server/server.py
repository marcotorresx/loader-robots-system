# TC2008B. Sistemas Multiagentes y Gráficas Computacionales
# Python flask server to interact with Unity. Based on the code provided by Sergio Ruiz.
# Octavio Navarro. October 2021

from flask import Flask, request, jsonify
from model import RandomModel
from agents.RandomAgent import RandomAgent
from agents.ObstacleAgent import ObstacleAgent
from agents.DestinyAgent import DestinyAgent
from agents.BoxAgent import BoxAgent

# Size of the board:
number_agents = 10
width = 28
height = 28
boxes = 20
randomModel = None
currentStep = 0

app = Flask("Robot Example")

# @app.route('/', methods=['POST', 'GET'])

@app.route('/init', methods=['POST', 'GET'])
def initModel():
    global currentStep, randomModel, number_agents, width, height, boxes

    if request.method == 'POST':
        number_agents = int(request.form.get('NAgents'))
        width = int(request.form.get('width'))
        height = int(request.form.get('height'))
        boxes = int(request.form.get('boxes'))
        currentStep = 0

        randomModel = RandomModel(number_agents, width, height, boxes)

        return jsonify({"message":"Parameters recieved, model initiated."})

@app.route('/getAgents', methods=['GET'])
def getAgents():
    global randomModel

    if request.method == 'GET':
        agentPositions = []
        for (w, x, z) in randomModel.grid.coord_iter():
            for agent in w:
                if isinstance(agent, RandomAgent):
                    agentPositions.append({"id": str(agent.unique_id), "x": x, "y":0, "z":z})
        
        return jsonify({'positions':agentPositions})

@app.route('/getBoxes', methods=['GET'])
def getBoxes():
    global randomModel

    if request.method == 'GET':
        agentPositions = []
        for (w, x, z) in randomModel.grid.coord_iter():
            for agent in w:
                if isinstance(agent, BoxAgent):
                    if agent.isTaken:
                        agentPositions.append({"id": str(agent.unique_id), "x": x, "y": 0.3, "z":z})
                    else:
                        agentPositions.append({"id": str(agent.unique_id), "x": x, "y": agent.order, "z":z})

        return jsonify({'positions':agentPositions})

@app.route('/getDestiny', methods=['GET'])
def getDestiny():
    global randomModel

    if request.method == 'GET':
        agentPositions = []
        for (w, x, z) in randomModel.grid.coord_iter():
            for agent in w:
                if isinstance(agent, DestinyAgent):
                    agentPositions.append({"id": str(agent.unique_id), "x": x, "y":0, "z":z})

        return jsonify({'positions':agentPositions})

@app.route('/getObstacles', methods=['GET'])
def getObstacles():
    global randomModel

    if request.method == 'GET':
        agentPositions = []
        for (w, x, z) in randomModel.grid.coord_iter():
            for agent in w:
                if isinstance(agent, ObstacleAgent):
                    agentPositions.append({"id": str(agent.unique_id), "x": x, "y":0, "z":z})

        return jsonify({'positions':agentPositions})

@app.route('/update', methods=['GET'])
def updateModel():
    global currentStep, randomModel
    if request.method == 'GET':
        randomModel.step()
        currentStep += 1
        return jsonify({'message':f'Model updated to step {currentStep}.', 'currentStep':currentStep})

if __name__=='__main__':
    app.run(host="localhost", port=8585, debug=True)