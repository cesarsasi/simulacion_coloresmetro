
from mesa import Agent
import math

#Cada estación se compone de [nombre estación, personas iniciales,personas que ingresan por step, color, capacidad estación]
#Color 0 = Común , 1 = Verde, 2 = Rojo
LISTA_ESTACIONES = [["Puente Alto",10,15,0,3000],["Las mercedes",10,15,2,3000],["Protectora de la infancia",10,15,1,3000],["Hospital Sotero del Rio",10,15,0,3000],["Elisa Correa",10,15,0,3000],["Los Quillayes",10,15,3,3000],["San José de la Estrella",10,15,2,3000],["Trinidad",10,15,3,3000],["Rojas Magallanes",10,15,2,3000],["Vicente Valdés",10,15,0,3000],["Vicuña Mackenna",10,15,0,3000],["Macul",10,15,0,3000],["Las Torres",10,15,3,3000],["Quilin",10,15,2,3000],["Los Presidentes",10,15,3,3000],["Grecia",10,15,2,3000],["Los Orientales",10,15,3,3000],["Plaza Egaña",10,15,0,3000],["Simón Bolivar",10,15,2,3000],["Principe de Gales",10,15,3,3000],["Francisco Bilbao",10,15,0,3000],["Cristóbal Colón",10,15,2,3000],["Tobalba",10,15,0,3000]]
LARGO_ANDEN = 50
POSX_ORIGEN = 0
POSY_ORIGEN = 0
POSY_FINAL  = 20
POSX_FINAL  = LARGO_ANDEN*len(LISTA_ESTACIONES)

CANT_PUERTAS = 4
CANT_TORNIQU = 3
CANT_ANDENES = len(LISTA_ESTACIONES)


POSY_MURO_ENTRADA = POSY_FINAL - int(math.floor(POSY_FINAL * .5))
POSY_MURO_TREN    = POSY_FINAL - int(math.floor(POSY_FINAL * .8))

POSY_I_TREN = LARGO_ANDEN - 2
POSY_F_TREN = POSY_FINAL - 1

ANCHO_TREN  = POSY_FINAL - int(math.floor(POSY_FINAL * .8)) -1
LARGO_TREN  = LARGO_ANDEN - 4

#Pasos en los que se abre la puerta
TIMERABRIR = 25 
#Pasos en los que se cierra la puerta
TIMERCERRAR = 20 

CANT_P_PUERTACARRO = 5
CANT_P_TORNIQUETE = 1

class Construccion(Agent):
    def __init__(self,model, pos, transitable):
        super().__init__(self,model)
        self.pos = pos
        self.transitable = transitable
    def get_position(self):
        return self.pos
    # def step(self):
    #     print("h")

class Muro(Construccion):
    def __init__(self, model, pos,transitable):
        super().__init__( model, pos, transitable)
    #def step(self):
        #print("Soy un muro") 
class AccesoEntrada(Construccion):
    def __init__(self, model, pos, transitable):
        super().__init__(model, pos, transitable)

class AccesoSalida(Construccion):
    def __init__(self, model, pos, transitable):
        super().__init__(model, pos, transitable)

class Puerta(Construccion):
    def __init__(self, model, pos, transitable):
        super().__init__( model, pos, transitable)
        self.cerrada = True
        self.contador = 0

class Pasajero(Agent):
    def __init__(self, model, pos):
        super().__init__(self,model)
        self.pos = pos
        self.direccion = self.set_direction()
        self.estacionOrigen = 0
        self.pasoAccesoEntrada = False
        self.pasoAccesoSalida = False
        self.salioVagon = False
        self.entroVagon = False

    def get_position(self):
        return self.pos
    
    def set_direction(self):
        if self.pos[1] < POSY_MURO_TREN:
            #False caminan hacia arriba
            return False 
        elif self.pos[1] >= POSY_MURO_TREN:
            #True caminan hacia abajo
            return True 
        else:
            print("[ERROR]: Algo salio mal al caminar")
    
    # Direccion Puertas
    def elegirPuerta(self,modelo, posPasajero):
        distancias = []
        puertas = modelo.getPuertas()
        for puerta in puertas:
            distancias.append( math.pow( posPasajero[0] - puerta[0], 2) + math.pow(posPasajero[1] - puerta[1], 2) )
        return puertas[ distancias.index(min(distancias)) ] 

    # Direccion accesos
    def elegirAcceso(self,modelo, posPasajero, direccion):
        distancias = []
        if direccion:
            accesos = modelo.getAccesosEntrada()
        else:
            accesos = modelo.getAccesosSalida()
        for acceso in accesos:
            distancias.append( math.pow( posPasajero[0] - acceso[0], 2) + math.pow(posPasajero[1] - acceso[1], 2) )
        return accesos[ distancias.index(min(distancias)) ] 

    def obtenerDestinosPosibles(self,accesoDestino, direccion):
        destinosPosibles = []
        vecindad = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False, radius = 1)
        for vecino in vecindad:
            pasajerosCerca = self.model.grid.get_neighbors(vecino,moore=True, include_center=True,radius=0)
            vecinos = [x for x in pasajerosCerca if type(x) is Pasajero and x!=self]
            if len(vecinos) < 3:
                destinosPosibles.append(vecino)
                obstaculosCerca = self.model.grid.get_neighbors(vecino,moore=True, include_center=True,radius=0)
                if direccion:
                    obstaculos = [x for x in pasajerosCerca if type(x) is not Pasajero and x!=self if type(x) is not AccesoEntrada] 
                else: 
                    obstaculos = [x for x in pasajerosCerca if type(x) is not Pasajero and x!=self if type(x) is not AccesoSalida] 
                if len(obstaculos) > 0:
                    destinosPosibles.remove(vecino)
        if accesoDestino in destinosPosibles:
            ObjetosEnAcceso = self.model.grid.get_neighbors(accesoDestino,moore=True, include_center=True,radius=0)
            PasajerosEnAcceso = [x for x in ObjetosEnAcceso if type(x) is Pasajero and x!=self]
            if len(PasajerosEnAcceso) > CANT_P_TORNIQUETE:
                return [self.pos]
            else:
                return [accesoDestino]
        if destinosPosibles == []:
            destinosPosibles.append(self.pos)
        return destinosPosibles

    def obtenerDestino(self, destinosPosibles, accesoDestino):
        distancias = [] 
        for destinoSiguiente in destinosPosibles:
             distancias.append( math.pow( destinoSiguiente[0] - accesoDestino[0], 2) + math.pow(destinoSiguiente[1] - accesoDestino[1], 2) )
        return destinosPosibles[ distancias.index(min(distancias)) ]

    def obtenerDestinosPosiblesPuertas(self,puertaDestino):
            destinosPosibles = []
            puerta = []
            vecindad = self.model.grid.get_neighborhood(self.pos,moore=True,include_center=False, radius = 1)
            for vecino in vecindad:
                cosasCerca = self.model.grid.get_neighbors(vecino,moore=True, include_center=True,radius=0)
                vecinos = [x for x in cosasCerca if type(x) is Pasajero and x!=self]
                obstaculos = [x for x in cosasCerca if type(x) is not Pasajero and x!=self if type(x) is not Puerta]               
                puerta =  [x for x in cosasCerca if type(x) is Puerta]
                if len(vecinos) < 3:
                    destinosPosibles.append(vecino)
                    if len(obstaculos) > 0:
                        destinosPosibles.remove(vecino)
            if puertaDestino in destinosPosibles:
                ObjetosEnPuerta = self.model.grid.get_neighbors(puertaDestino,moore=True, include_center=True,radius=0)
                PasajerosEnPuerta = [x for x in ObjetosEnPuerta if type(x) is Pasajero and x!=self]
                if len(PasajerosEnPuerta) > CANT_P_PUERTACARRO:
                    return [self.pos]
                else:
                    return [puertaDestino]
            if destinosPosibles == []:
                destinosPosibles.append(self.pos)
            return destinosPosibles

    # Direccion al interior del carro
    def elegirUInterior(self,modelo, posPasajero):
        distancias = []
        uInteriores = modelo.getUInteriores()
        for uInterior in uInteriores:
            distancias.append( math.pow( posPasajero[0] - uInterior[0], 2) + math.pow(posPasajero[1] - uInterior[1], 2) )
        return uInteriores[ distancias.index(min(distancias)) ] 

    # En cada step
    def step(self):
        if self.pos in self.model.posPuertas and self.direccion and not self.entroVagon:
            self.entroVagon = True
            self.model.pasajerosEntraronCarro+=1
        elif self.pos in self.model.posPuertas and not self.direccion and not self.salioVagon:
            self.salioVagon = True
            self.model.pasajerosSalieronCarro+=1
        elif self.pos in self.model.posAccesosEntrada and self.direccion and not self.pasoAccesoEntrada:
            self.pasoAccesoEntrada = True
            self.model.pasajerosEntraronAccesos+=1
        elif self.pos in self.model.posAccesosSalida and not self.direccion and not self.pasoAccesoEntrada:
            self.pasoAccesoSalida = True
            self.model.pasajerosSalieronAccesos+=1
        if self.pos[0] == POSX_ORIGEN or self.pos[0] == POSX_FINAL -1  or self.pos[1] == POSY_ORIGEN or self.pos[1] == POSY_FINAL -1:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
        elif self.model.contador == TIMERCERRAR -1 and self.pos[1] < POSY_MURO_TREN +1 and not self.model.puertas[0].cerrada:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
        elif self.model.contador == TIMERCERRAR -1 and self.pos[1] == POSY_MURO_TREN +1 and not self.model.puertas[0].cerrada and self.direccion:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            
        else:
            #Fuera de los accesos
            if self.pos[1] > POSY_MURO_ENTRADA and self.direccion == True: 
                accesoDestino = self.elegirAcceso(self.model, self.pos, self.direccion)
                destinosPosibles = self.obtenerDestinosPosibles(accesoDestino, self.direccion)
                destino = self.obtenerDestino(destinosPosibles,accesoDestino)
            #Dentro de la estacion direccion puerta
            elif self.pos[1] <= POSY_MURO_ENTRADA and self.pos[1] > POSY_MURO_TREN and self.direccion == True: 
                PuertaDestino = self.elegirPuerta(self.model, self.pos)
                destinosPosibles = self.obtenerDestinosPosiblesPuertas(PuertaDestino)
                destino = self.obtenerDestino(destinosPosibles,PuertaDestino)
                if PuertaDestino == destino:
                    ObjetosEnPuerta = self.model.grid.get_neighbors(destino,moore=True, include_center=True,radius=0)
                    ListaPuerta = [x for x in ObjetosEnPuerta if type(x) is Puerta]
                    if ListaPuerta[0].cerrada == True:
                        destino = self.pos
            #En la puerta ingresando al tren
            elif self.pos[1] <= POSY_MURO_TREN and self.direccion == True: 
                centroDestino = self.elegirUInterior(self.model, self.pos)
                destinosPosibles = self.obtenerDestinosPosiblesPuertas(centroDestino)
                destino = self.obtenerDestino(destinosPosibles,centroDestino)
            #En el tren y van a salir
            elif self.pos[1] < POSY_MURO_TREN and self.direccion == False:
                PuertaDestino = self.elegirPuerta(self.model, self.pos)
                destinosPosibles = self.obtenerDestinosPosiblesPuertas(PuertaDestino)
                destino = self.obtenerDestino(destinosPosibles,PuertaDestino)
                if PuertaDestino == destino:
                    ObjetosEnPuerta = self.model.grid.get_neighbors(destino,moore=True, include_center=True,radius=0)
                    ListaPuerta = [x for x in ObjetosEnPuerta if type(x) is Puerta]
                    if ListaPuerta[0].cerrada == True:
                        destino = self.pos
            #Dentro de la estacion direccion acceso
            elif self.pos[1] < POSY_MURO_ENTRADA and self.pos[1] >= POSY_MURO_TREN and self.direccion == False:
                accesoDestino = self.elegirAcceso(self.model, self.pos, self.direccion)
                destinosPosibles = self.obtenerDestinosPosibles(accesoDestino,self.direccion)
                destino = self.obtenerDestino(destinosPosibles,accesoDestino)
            elif self.pos[1] >= POSY_MURO_ENTRADA and self.direccion == False:
                destino = (self.pos[0] , self.pos[1] +1)
            else:
                destino = (0,0)
            self.model.grid.move_agent(self,destino)

class Tren(Agent):
    def __init__(self, model, pos):
        super().__init__(self,model)
        self.servicio = True
        self.capacidadUsuarios = 0
        self.cantidadUsuarios = 0
        self.colorRuta = 0
        self.valorPuerta = False
        self.direccion = False
        self.pos = pos
        self.estacionActual = 0
        self.estacionSiguiente = 0
        self.estacionObjetivo = 0
    
    def step(self):
        print("Comenzar step Vagon")

        #Movimiento
        desplaNuevaEstacion = self.pos[0]+ LARGO_ANDEN
        destino = (desplaNuevaEstacion, self.pos[1])
        
        # self.pos = destino
        if destino[0] < POSX_FINAL:
            print("POS O",self.pos)
            print("POS D", destino)
            self.model.grid.move_agent(self,destino)
        else: 
            print("Tren llego al final")

        # abrirPuertas(self,pasajerosEntrantes, colorEstacion)
        # avanzarTren(self)
    
    def abrirPuertas(self, pasajerosEntrantes, colorEstacion):
        if self.valorPuerta == False and colorEstacion == self.colorRuta and self.servicio == True:  
            self.valorPuerta = True
            # Liberar Pasajeros

            # Tomar Pasajaros
            if self.capacidadUsuarios > self.cantidadUsuarios :
                capacidadDisponible = self.capacidadUsuarios - self.cantidadUsuarios
                # Tomar capacidadDisponible usuarios como maximo
                if pasajerosEntrantes < capacidadDisponible:
                    self.cantidadUsuarios += pasajerosEntrantes
                    print ("Tren capta total de pasajeros, tomados : ", pasajerosEntrantes)
                else:
                    self.cantidadUsuarios += capacidadDisponible
                    print ("Tren capta parcialmente pasajeros, abandonados : ", (pasajerosEntrantes-capacidadDisponible) )
            self.valorPuerta = True

    def cerrarPuertas(self):
        if self.valorPuerta == True:  self.valorPuerta = False

    def avanzarTren(self, estadoEstacion):
        if  estadoEstacion == True and self.estacionObjetivo != self.estacionActual and self.servicio == True:  
            self.estacionActual +=1
            self.estacionSiguiente +=1
            print ("Tren transportado")
        if  estadoEstacion == False:
            print ("Tren no transportado: Siguiente estacion Ocupada")
        else:
            self.servicio = False
            print ("Tren Liberado")
    

class Estacion():
    def __init__(self, model, pos):
        super().__init__(self,model)
        self.nombreEstacion = ""
        self.disponibilidadEstacion  = True
        self.haytren  = False
        self.flujoEntrada = 0
        self.flujoSalida  = 0
        self.capacidadUsuarios = 0
        self.cantidadUsuarios = 0
        self.colorEstacion = 0
        self.idEstacion=0


