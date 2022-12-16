from mesa.visualization.modules import CanvasGrid # viz of grid
from mesa.visualization.ModularVisualization import ModularServer #server
from mesa.visualization.modules import ChartModule
from mesa.visualization.UserParam import UserSettableParameter
from model import miModelo #our model
from agent import Pasajero, Muro, AccesoEntrada, AccesoSalida, Puerta, Tren
from agent import POSX_FINAL, POSY_FINAL, ANCHO_TREN, LARGO_TREN

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
    elif type(agent) is Tren:
        portrayal["Layer"] = 1
        portrayal["Shape"] = "rect"
        portrayal["Filled"] = "true"
        portrayal["w"] = LARGO_TREN+3
        portrayal["h"] = ANCHO_TREN
        # color 2 = Común , 1 = Verde, 0 = Rojo
        if agent.colorRuta == 0:
            portrayal["Color"] = "red"
        else:
            portrayal["Color"] = "green"
    return portrayal 
grid = CanvasGrid(agent_portrayal,POSX_FINAL,POSY_FINAL,POSX_FINAL*4,POSY_FINAL*4)

chart = ChartModule([{"Label": "Plaza puente alto",
                        "Color": "Blue"},
                    {"Label": "Las Mercedes",
                        "Color": "Red"},
                    {"Label": "Protectora de la infancia",
                        "Color": "Yellow"},
                    {"Label": "Hospital Sotero del Rio",
                        "Color": "Green"},
                    {"Label": "Elisa Correa",
                        "Color": "Pink"},
                    {"Label": "Los Quillayes",
                        "Color": "MediumVioletRed"},
                    {"Label": "San José de la Estrella",
                        "Color": "Orange"},
                    {"Label": "Trinidad",
                        "Color": "Khaki"},
                    {"Label": "Rojas Magallanes",
                        "Color": "Lavender"},
                    {"Label": "Vicente Valdés",
                        "Color": "Purple"},
                    {"Label": "Vicuña Mackenna",
                        "Color": "Lime"},
                    {"Label": "Macul",
                        "Color": "Olive"},
                    {"Label": "Las Torres",
                        "Color": "Teal"},
                    {"Label": "Quilin",
                        "Color": "Cyan"},
                    {"Label": "Los Presidentes",
                        "Color": "Navy"},
                    {"Label": "Grecia",
                        "Color": "Peru"},
                    {"Label": "Los Orientales",
                        "Color": "SaddleBrown"},
                    {"Label": "Plaza Egaña",
                        "Color": "Brown"},
                    {"Label": "Simón Bolivar",
                        "Color": "Grey"},
                    {"Label": "Principe de Gales",
                        "Color": "DimGrey"},
                    {"Label": "Francisco Bilbao",
                        "Color": "DarkSlateGray"},
                    {"Label": "Cristóbal Colón",
                        "Color": "Sienna"},
                    {"Label": "Tobalba",
                        "Color": "Black"}],
                    data_collector_name='datacollector')

server = ModularServer(miModelo,
                       [grid,chart],
                       "Simulacion colores metro santiago",
                       {"N_Pasajeros":N_PASAJEROS_INICIALES})  