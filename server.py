from mesa.visualization.modules import CanvasGrid # viz of grid
from mesa.visualization.ModularVisualization import ModularServer #server
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from model import miModelo #our model
from agent import Pasajero, Muro, AccesoEntrada, AccesoSalida, Puerta
from agent import POSX_FINAL, POSY_FINAL

N_PASAJEROS_INICIALES = 1000
def agent_portrayal(agent): 
    if agent is None:
        print("[ERROR] : No existen agentes.")
        return
    #(x, y) = agent.get_position()
    #portrayal["x"] = x
    #portrayal["y"] = y

    # portrayal = {"Shape": "circle",
    #     "Filled": "true",
    #     "Layer": 0,
    #     "Color": "red",
    #     "r": 0.5}
    # return portrayal 
    portrayal = {}
    if type(agent) is Pasajero:
        portrayal["Layer"] = 1
        portrayal["scale"] = .8
        portrayal["Shape"] = "./resources/pasajero.png"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "orange"
        portrayal["r"] = 0.5
    elif type(agent) is Muro:
        portrayal["Layer"] = 1
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "black"
        portrayal["w"] = 1
        portrayal["h"] = 1
    elif type(agent) is AccesoEntrada:
        portrayal["Layer"] = 1
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "green"
        portrayal["w"] = 1
        portrayal["h"] = 1
    elif type(agent) is AccesoSalida:
        portrayal["Layer"] = 1
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "red"
        portrayal["w"] = 1
        portrayal["h"] = 1
    elif type(agent) is Puerta:
        portrayal["Layer"] = 1
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["Color"] = "yellow"
        portrayal["w"] = 1
        portrayal["h"] = 1
    return portrayal
grid = CanvasGrid(agent_portrayal,POSX_FINAL,POSY_FINAL,1000,500)
#chart = ChartModule([{"Label":"Nagentes","Color":"red"}],data_collector_name="datacollector")

server = ModularServer(miModelo,
                       [grid],
                       "Simulacion colores metro santiago",
                       {"N_Pasajeros":N_PASAJEROS_INICIALES})  