from mesa import Model 
from mesa.time import RandomActivation 
from mesa.space import MultiGrid
from agent import Pasajero, Construccion, Muro, AccesoEntrada, AccesoSalida, Puerta, Tren
#Importar las constantes de los agentes
from agent import POSX_ORIGEN, POSX_FINAL, POSY_ORIGEN, POSY_FINAL, CANT_ANDENES, CANT_PUERTAS, CANT_TORNIQU, POSY_MURO_ENTRADA,POSY_MURO_TREN, LISTA_ESTACIONES, TIMERCERRAR, LARGO_ANDEN, POSY_I_TREN
import numpy as np
import csv 
import matplotlib.pyplot as plt
import math 
import time
from random import randrange

#La cantidad de pasajeros que van apareciendo y se dirigen a los accesos
P_ENTRANDO_ESTACION = 3
#Cantidad mínima de pasajeros que llegan dentro del carro
MIN_P_CARRO = 30 
#Cantidad máxima de pasajeros que llegan dentro del carro
MAN_P_CARRO = 50 




class miModelo(Model):
    def __init__(self,N_Pasajeros): #constructor, metemos el argumento Número Pasajeros iniciales
        self.running = True #permite la ejecución continua 
        self.schedule = RandomActivation(self) # elige el tipo de schedule   
        self.grid = MultiGrid(POSX_FINAL,POSY_FINAL,False) #tipo y tamaño de grid

        self.posAccesosEntrada = [] #guarda las posiciones de los torniquites de entrada
        self.posAccesosSalida = [] #guarda las posiciones de los torniquites de salida
        self.posPuertas = [] #guarda las posiciones de las puertas
        self.puertas = [] #guarda los objetos puerta
        self.posTrenes = [] #guarda las posiciones de los trenes
        self.trenes = [] #guarda los objetos tren
        self.cronogramaPasajeros = []  #orden y lugar de llegada, junto a destino de pasajeros
        self.saturacionEstaciones = []

        self.posUInteriores = calcularUInteriores() #te calcula todas las posiciones interios del vagón a donde se dirigen los usuarios
        
        self.contador = 1 # contador de ticks para abrir y cerrar puertas
        self.pasajerosEntraronAccesos = 0 #contador para pasajeros que entran a accesos
        self.pasajerosSalieronAccesos = 0 #contador para pasajeros que entran a accesos
        self.pasajerosEntraronCarro = 0 #contador para pasajeros que entran a accesos
        self.pasajerosSalieronCarro = 0 #contador para pasajeros que entran a accesos
        self.colorRuta = 0
        #self.timer = TIMERABIERTO
        
        # Carga de pasajeros
        cargarDatos(self)

        # Dibujar limites
        dibujarAccesos(self) 
        dibujarPuertas(self) 
        # print("PUERTAS", self.puertas)
        dibujarMuros(self)  
        dibujarPasajeros(self,N_Pasajeros, False)
        dibujarTren(self,1)
        
        # a = Puerta(self,(1,1))
        # self.schedule.add(a)
        # #Dibuja el agente pasajero
        # self.grid.place_agent(a, a.pos)

    def step(self):
        print("Comenzar step")
        self.schedule.step()

        dibujarNuevosPasajeros(self,1,self.contador)

        dibujarTren(self,1)
        
        if self.schedule.get_agent_count()<2:
            self.running = False
        self.contador +=1
        self.saturacionEstaciones = []
        for i in range (0,len(LISTA_ESTACIONES)):
            pasajero_anden = obtenerPasajerosEnRango(self, i*LARGO_ANDEN,i*LARGO_ANDEN +LARGO_ANDEN, POSY_MURO_TREN,POSY_MURO_ENTRADA)
            self.saturacionEstaciones.append(pasajero_anden)
        # print("SAT", self.saturacionEstaciones)

        # pasajerosAEntrar = []
        # pasajerosASalir = []

        print("Los pasajeros que han entrado por los accesos son ", self.pasajerosEntraronAccesos)
        print("Los pasajeros que han salido por los accesos son ", self.pasajerosSalieronAccesos)
        # print("Los Pasajeros que han entrado al carro son ", self.pasajerosEntraronCarro)
        # print("Los Pasajeros que han salido del carro son ", self.pasajerosSalieronCarro)
        print("---- Terminar step ----")

    def getAccesosEntrada(self):
        return self.posAccesosEntrada
    def getPuertas(self, ind):
        return self.puertas[ind]
    def getTrenes(self):
        return self.posTrenes
    def getUInteriores(self):
        return self.posUInteriores
    def getAccesosSalida(self):
        return self.posAccesosSalida
    

def cargarDatos(modelo):
    with open('viajes.csv', 'r') as f:
        data = list(csv.reader(f, delimiter=","))

    dataarray = np.array(data)
    dataarray = np.delete(dataarray,(0), axis = 0)
    dataarray[dataarray[:,2].argsort()]

    tini= dataarray[0][2].split(':')
    tfin= dataarray[-1][2].split(':')



    ini = int(tini[0])*60*60 + int(tini[1])*60 + int(tini[2])
    fin = int(tfin[0])*60*60 + int(tfin[1])*60 + int(tfin[2])

    ticks = int((fin-ini)/15)
    print("[TICKS]:", ticks)

    cont = 0
    for registro in dataarray:
        texreg= registro[2].split(':')
        timereg = int(texreg[0])*60*60 + int(texreg[1])*60 + int(texreg[2])
        dataarray[cont][2] = timereg
        cont = cont+1

    list_ticks = [[]]
    time = int(ini) + 15
    conta = 0
    for registro in dataarray:
        timep = int(registro[2])
        subida = int(registro[6])
        bajada = int(registro[7])

        if timep < time:
            list_ticks[conta].append([subida,bajada])
        else:
            time = time + 15
            conta = conta + 1
            list_ticks.append([])
            list_ticks[conta].append([subida,bajada])

        # print('SEG', registro[2]) 

    modelo.cronogramaPasajeros = list_ticks
                
def dibujarMuros(modelo):
    # Extremos
    #Sup, Inf, Izq y Der respectivamente
    dibujarMuro(modelo, POSX_ORIGEN, POSX_FINAL, POSY_FINAL - 1, POSY_FINAL - 1)
    dibujarMuro(modelo, POSX_ORIGEN, POSX_FINAL, POSY_ORIGEN,  POSY_ORIGEN)
    dibujarMuro(modelo, POSX_ORIGEN, POSX_ORIGEN, POSY_ORIGEN+1, POSY_FINAL-1)
    dibujarMuro(modelo, POSX_FINAL -1, POSX_FINAL -1, POSY_ORIGEN, POSY_FINAL-1) 

    # Accesos a la estacion
    #Accesos .5 de distancia
    dibujarMuro(modelo, POSX_ORIGEN, POSX_FINAL, POSY_MURO_ENTRADA, POSY_MURO_ENTRADA)
    #Tren .8 de distancia
    dibujarMuro(modelo, POSX_ORIGEN, POSX_FINAL, POSY_MURO_TREN, POSY_MURO_TREN)    
              
    # Separar Estaciones
    largoAnden = (int)(POSX_FINAL/CANT_ANDENES)
    for muro in range(CANT_ANDENES-1):
        posX = (int)((largoAnden)*(muro+1))
        dibujarMuro(modelo, posX, posX, POSY_ORIGEN+1, POSY_FINAL-1)
    
def dibujarMuro(modelo, inicial_x, final_x, inicial_y, final_y):
    if inicial_y == final_y:
        for i in range(inicial_x,final_x):
            a = Muro(modelo,(i,inicial_y), False)
            vecinos = modelo.grid.get_neighbors(a.pos,moore=True, include_center=True,radius=0)
            vecinos = [x for x in vecinos if type(x) is AccesoEntrada or AccesoSalida or Puerta]
            if vecinos==[]:
                modelo.grid.place_agent(a, a.pos)
                modelo.schedule.add(a)        
    elif inicial_x == final_x:
        for i in range(inicial_y,final_y):
            a = Muro(modelo,(inicial_x,i),False)
            modelo.schedule.add(a)
            modelo.grid.place_agent(a, a.pos)
    else:
        print("[ERROR]: Dibujando muro")

def dibujarAccesos(modelo):
    largoAnden = (int)(POSX_FINAL/CANT_ANDENES)
    # Ubicacion de los accesos
    XTORNIQUETE_IZQ = math.floor(largoAnden * .3) 
    XTORNIQUETE_CTR = math.floor(largoAnden * .5)
    XTORNIQUETE_DER = math.floor(largoAnden * .7)
    for anden in range(CANT_ANDENES):
        # print("HOLA")
        andenx = (int)((largoAnden)*(anden))
        # Acceso Salida (4)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_DER,POSY_MURO_ENTRADA,False)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_DER+1,POSY_MURO_ENTRADA, False)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_IZQ,POSY_MURO_ENTRADA, False)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_IZQ-1,POSY_MURO_ENTRADA, False)
        # Accesos Entrada (3)
        for i in range(0,CANT_TORNIQU):
            dibujarAcceso(modelo,andenx+XTORNIQUETE_CTR+i-4,POSY_MURO_ENTRADA, True)

def dibujarAcceso(modelo, pos_x,pos_y,EoS): 
    #EoS es Entrada (True), Salida (False)
    #True/Transitable False/NoTransitable
    if EoS:
        a = AccesoEntrada(modelo,(pos_x,pos_y),True) 
    else:
        a = AccesoSalida(modelo,(pos_x,pos_y),True)
    modelo.schedule.add(a)
    modelo.grid.place_agent(a, a.pos)
    if EoS:
        modelo.posAccesosEntrada.append(a.pos)
    else:
        modelo.posAccesosSalida.append(a.pos)

def dibujarPuertas(modelo):
    largoAnden = (int)(POSX_FINAL/CANT_ANDENES)
    # Ubicacion de las puertas
    cont_p = 0
    for anden in range(CANT_ANDENES):
        andenx = (int)((largoAnden)*(anden))
        modelo.puertas.append([])
        modelo.posPuertas.append([])
        for puerta in range(CANT_PUERTAS+1):
            if(puerta != 0):
                xPuerta = (int)(math.floor(largoAnden * ( .04 * (puerta))))
                #print("CONT P", cont_p)
                dibujarPuerta(modelo,xPuerta + andenx ,POSY_MURO_TREN, cont_p)
        cont_p=cont_p+1
        


def dibujarPuerta(modelo, pos_x,pos_y,cont):
    a = Puerta(modelo,(pos_x,pos_y),True)
    modelo.schedule.add(a)
    modelo.grid.place_agent(a, a.pos)
    modelo.posPuertas[cont].append(a.pos)
    modelo.puertas[cont].append(a)

def dibujarPasajeros(modelo,N_Pasajeros,step):
    contador = 0
    while contador < N_Pasajeros:
        # Creacion
        if step == False:
            pos_x = modelo.random.randint(POSX_ORIGEN + 1,POSX_FINAL - 2)
            estacionComienzo = math.floor(pos_x/LARGO_ANDEN)
            pos_y = modelo.random.randint(POSY_MURO_TREN + 1 ,POSY_FINAL - 2)
            estacionDestino = modelo.random.randint(estacionComienzo,CANT_ANDENES)
        # Steps genericos
        else:
            pos_x = modelo.random.randint(POSX_ORIGEN + 1,POSX_FINAL - 2)
            estacionComienzo = math.floor(pos_x/LARGO_ANDEN)
            pos_y = modelo.random.randint(POSY_ORIGEN + 1 ,POSY_MURO_TREN - 1)
            estacionDestino = modelo.random.randint(estacionComienzo,CANT_ANDENES)
        if pos_y != POSY_MURO_ENTRADA and pos_y !=  POSY_MURO_TREN and int(estacionDestino) != 0:
            contador+=1
            #Crear pasajero
            a = Pasajero(modelo,(pos_x,pos_y), estacionComienzo, estacionDestino)
            modelo.schedule.add(a)
            #Dibuja el agente pasajero
            modelo.grid.place_agent(a, a.pos)

def dibujarTren(modelo,N_Trenes):
    pos_x = POSY_I_TREN
    print("Pos Tren", pos_x)
    pos_y = 1
    vecinos = modelo.grid.get_neighbors((POSY_I_TREN,1),moore=True, include_center=True,radius=0)
    vecinos = [x for x in vecinos if type(x) is Tren ]
    if vecinos==[]:
        print("Soy un nuevo tren")
        modelo.colorRuta = modelo.colorRuta+1
        print("XY", pos_x, pos_y)

        a = Tren(modelo,(pos_x,pos_y),len(modelo.trenes),(modelo.colorRuta%2))
        modelo.schedule.add(a)
        modelo.posPuertas.append(a.pos)
        modelo.trenes.append(a)
        modelo.grid.place_agent(a, a.pos)
            
            

def dibujarNuevosPasajeros(modelo,N_Pasajeros,cont):
    # Dibuja pasajeros entrantes
    for i in range (0,len(modelo.cronogramaPasajeros[cont])):
        # pos_x = (int)(modelo.cronogramaPasajeros[cont][i][0]*LARGO_ANDEN + (LARGO_ANDEN*.7))
        estacionComienzo = modelo.cronogramaPasajeros[cont][i][0]
        pos_x = modelo.random.randint(estacionComienzo*LARGO_ANDEN +1 ,estacionComienzo*LARGO_ANDEN + LARGO_ANDEN - 1)
        estacionDestino = modelo.cronogramaPasajeros[cont][i][1]
        pos_y = POSY_FINAL -2

        if pos_y != POSY_MURO_ENTRADA and pos_y !=  POSY_MURO_TREN and int(estacionDestino) != 0:
            a = Pasajero(modelo,(pos_x,pos_y), estacionComienzo, estacionDestino)
            modelo.schedule.add(a)
            modelo.grid.place_agent(a, a.pos)

def calcularUInteriores():
    i = .1
    lista = []
    while POSX_FINAL * i < POSX_FINAL:
        lista.append( ( round (POSX_FINAL * i)  , ( math.floor(POSY_MURO_TREN*.5)  )) )
        i = i + .2
    return lista

def obtenerPasajerosEnRango(modelo,xinicial,xfinal, yinicial,yfinal):
        totalPasajeros = 0
        for x in range(xinicial,xfinal + 1):
            for y in range(yinicial,yfinal):
                pos = (x,y)
                pasajeros = modelo.grid.get_neighbors( pos,moore=True, include_center=True,radius=0)
                pasajeros = [x for x in pasajeros if type(x) is Pasajero]
                totalPasajeros += len(pasajeros)
        return totalPasajeros