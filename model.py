from mesa import Model 
from mesa.time import RandomActivation 
from mesa.space import MultiGrid
from agent import Pasajero, Construccion, Muro, AccesoEntrada, AccesoSalida, Puerta
#Importar las constantes de los agentes
from agent import POSX_ORIGEN, POSX_FINAL, POSY_ORIGEN, POSY_FINAL, CANT_ANDENES, CANT_PUERTAS, CANT_TORNIQU, POSY_MURO_ENTRADA,POSY_MURO_TREN, TIMERABRIR, TIMERCERRAR

import math 
import time
from random import randrange

#La cantidad de pasajeros que van apareciendo y se dirigen a los accesos
P_ENTRANDO_ESTACION = 10 
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

        self.posUInteriores = calcularUInteriores() #te calcula todas las posiciones interios del vagón a donde se dirigen los usuarios
        
        self.contador = 1 # contador de ticks para abrir y cerrar puertas
        self.pasajerosEntraronAccesos = 0 #contador para pasajeros que entran a accesos
        self.pasajerosSalieronAccesos = 0 #contador para pasajeros que entran a accesos
        self.pasajerosEntraronCarro = 0 #contador para pasajeros que entran a accesos
        self.pasajerosSalieronCarro = 0 #contador para pasajeros que entran a accesos
        #self.timer = TIMERABIERTO

        # Dibujar limites
        dibujarAccesos(self) 
        dibujarPuertas(self) 
        dibujarMuros(self)  
        dibujarPasajeros(self,N_Pasajeros, False)

    def step(self):
        print("Comenzar step")
        self.schedule.step()
        dibujarNuevosPasajeros(self,1)
        # N_Pasajeros = self.random.randint(1,12)
        if self.schedule.get_agent_count()<2:
            self.running = False
        self.contador +=1
        pasajerosAEntrar = []
        pasajerosASalir = []
        if self.contador == TIMERABRIR and self.puertas[0].cerrada:
            pasajerosAEntrar = self.obtenerPasajerosEnRango(POSX_ORIGEN,POSX_FINAL, POSY_MURO_TREN,POSY_MURO_ENTRADA)
            print("PASAJEROS A ENTRAR ", len(pasajerosAEntrar))
            time.sleep(5)
            for puerta in self.puertas:
                puerta.cerrada =  False
                self.contador = 0
            #Pasajeros que aparecen en el vagon
            dibujarPasajeros(self, self.random.randint(MIN_P_CARRO,MAN_P_CARRO), True) 
        elif self.contador == TIMERCERRAR and not self.puertas[0].cerrada:
            for puerta in self.puertas:
                puerta.cerrada =  True
                self.contador = 0
        elif self.contador == TIMERCERRAR -1 and not self.puertas[0].cerrada:
            pasajerosEntraron = self.obtenerPasajerosEnRango(POSX_ORIGEN,POSX_FINAL, POSY_ORIGEN+1,POSY_MURO_TREN)
            pasajerosNoEntraron = self.obtenerPasajerosEnRango(POSX_ORIGEN,POSX_FINAL, POSY_MURO_TREN,POSY_MURO_ENTRADA)
            print("PASAJEROS QUE ENTRARON ", len(pasajerosEntraron))
            print("PASAJEROS QUE NO ENTRARON", len(pasajerosNoEntraron))
            time.sleep(5)
        print("Los pasajeros que han entrado por los accesos son ", self.pasajerosEntraronAccesos)
        print("Los pasajeros que han salido por los accesos son ", self.pasajerosSalieronAccesos)
        print("Los Pasajeros que han entrado al carro son ", self.pasajerosEntraronCarro)
        print("Los Pasajeros que han salido del carro son ", self.pasajerosSalieronCarro)
        print("---- Terminar step ----")

    def getAccesosEntrada(self):
        return self.posAccesosEntrada
    def getPuertas(self):
        return self.posPuertas
    def getUInteriores(self):
        return self.posUInteriores
    def getAccesosSalida(self):
        return self.posAccesosSalida
    def obtenerPasajerosEnRango(self,xinicial,xfinal, yinicial,yfinal):
        totalPasajeros = []
        for x in range(xinicial,xfinal + 1):
            for y in range(yinicial,yfinal):
                pos = (x,y)
                pasajeros = self.grid.get_neighbors( pos,moore=True, include_center=True,radius=0)
                pasajeros = [x for x in pasajeros if type(x) is Pasajero and x.direccion == True]
                if len(pasajeros) > 0:
                    totalPasajeros = totalPasajeros + pasajeros
        return totalPasajeros

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
        andenx = (int)((largoAnden)*(anden))
        # Acceso Salida (4)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_DER,POSY_MURO_ENTRADA,False)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_DER+1,POSY_MURO_ENTRADA, False)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_IZQ,POSY_MURO_ENTRADA, False)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_IZQ-1,POSY_MURO_ENTRADA, False)
        # Accesos Entrada (3)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_CTR,POSY_MURO_ENTRADA, True)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_CTR+1,POSY_MURO_ENTRADA, True)
        dibujarAcceso(modelo,andenx+XTORNIQUETE_CTR-1,POSY_MURO_ENTRADA, True)

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
    for anden in range(CANT_ANDENES):
        andenx = (int)((largoAnden)*(anden))
        for puerta in range(CANT_PUERTAS+1):
            if(puerta != 0):
                xPuerta = (int)(math.floor(largoAnden * ( .2 * (puerta))))
                dibujarPuerta(modelo,xPuerta + andenx ,POSY_MURO_TREN)

def dibujarPuerta(modelo, pos_x,pos_y):
    a = Puerta(modelo,(pos_x,pos_y),True)
    modelo.schedule.add(a)
    modelo.grid.place_agent(a, a.pos)
    modelo.posPuertas.append(a.pos)
    modelo.puertas.append(a)

def dibujarPasajeros(modelo,N_Pasajeros,step):
    contador = 0
    while contador < N_Pasajeros:
        if step == False:
            pos_x = modelo.random.randint(POSX_ORIGEN + 1,POSX_FINAL - 2)
            pos_y = modelo.random.randint(POSY_MURO_TREN + 1 ,POSY_FINAL - 2)
        else:
            pos_x = modelo.random.randint(POSX_ORIGEN + 1,POSX_FINAL - 2)
            pos_y = modelo.random.randint(POSY_ORIGEN + 1 ,POSY_MURO_TREN - 1)
        if pos_y != POSY_MURO_ENTRADA and pos_y !=  POSY_MURO_TREN:
            contador+=1
            #Crear pasajero
            a = Pasajero(modelo,(pos_x,pos_y))
            modelo.schedule.add(a)
            #Dibuja el agente pasajero
            modelo.grid.place_agent(a, a.pos)
    

def dibujarNuevosPasajeros(modelo,N_Pasajeros):
    #while contador < N_Pasajeros:
    if modelo.random.randint(0,1):
        largoAnden = (int)(POSX_FINAL/CANT_ANDENES)
        for anden in range(CANT_ANDENES):
            estacion = (int)((largoAnden)*(anden))

            if modelo.random.randint(0,1):
                pos_x = (int)(estacion + (largoAnden*.3)) 
                pos_y = POSY_FINAL -2
                #contador+=1
            else:
                pos_x = (int)(estacion + (largoAnden*.7))
                pos_y = POSY_FINAL -2
            # Dibuja pasajeros entrantes
            for i in range (0,P_ENTRANDO_ESTACION):
                a = Pasajero(modelo,(pos_x,pos_y))
                modelo.schedule.add(a)
                modelo.grid.place_agent(a, a.pos)

def calcularUInteriores():
    i = .1
    lista = []
    while POSX_FINAL * i < POSX_FINAL:
        lista.append( ( round (POSX_FINAL * i)  , ( math.floor(POSY_MURO_TREN*.5)  )) )
        i = i + .2
    return lista

