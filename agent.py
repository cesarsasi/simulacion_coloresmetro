
from mesa import Agent
import math

#Cada estación se compone de [nombre estación, personas iniciales,personas que ingresan por step, color, capacidad estación]
#Color 0 = Común , 1 = Verde, 2 = Rojo
#Aolor 2 = Común , 1 = Verde, 0 = Rojo

LISTA_ESTACIONES = [["Puente Alto",10,15,2,1500],["Las mercedes",10,15,0,1500],["Protectora de la infancia",10,15,1,1500],["Hospital Sotero del Rio",10,15,2,1500],["Elisa Correa",10,15,2,1500],["Los Quillayes",10,15,1,1500],["San José de la Estrella",10,15,0,1500],["Trinidad",10,15,1,1500],["Rojas Magallanes",10,15,0,1500],["Vicente Valdés",10,15,2,1500],["Vicuña Mackenna",10,15,2,1500],["Macul",10,15,2,1500],["Las Torres",10,15,1,1500],["Quilin",10,15,0,1500],["Los Presidentes",10,15,1,1500],["Grecia",10,15,0,1500],["Los Orientales",10,15,1,1500],["Plaza Egaña",10,15,2,1500],["Simón Bolivar",10,15,0,1500],["Principe de Gales",10,15,1,1500],["Francisco Bilbao",10,15,2,1500],["Cristóbal Colón",10,15,0,1500],["Tobalba",10,15,2,1500]]

LARGO_ANDEN = 150
POSX_ORIGEN = 0
POSY_ORIGEN = 0
POSY_FINAL  = 50
POSX_FINAL  = LARGO_ANDEN*len(LISTA_ESTACIONES)

CANT_PUERTAS = 24
CANT_TORNIQU = 10
CANT_ANDENES = len(LISTA_ESTACIONES)

POSY_MURO_ENTRADA = 20
POSY_MURO_TREN    = 10

POSY_I_TREN = LARGO_ANDEN - 1
POSY_F_TREN = POSY_FINAL - 1

ANCHO_TREN  = POSY_FINAL - int(math.floor(POSY_FINAL * .8)) -1
LARGO_TREN  = LARGO_ANDEN - 4

#Pasos en los que se abre la puerta
TIMERABRIR = 2
#Pasos en los que se cierra la puerta
TIMERCERRAR = 6

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
    def get_pos(self):
        return self.pos

class Pasajero(Agent):
    def __init__(self, model, pos, estacionOrigen, estacionDestino):
        super().__init__(self,model)
        self.pos = pos
        self.direccion = self.set_direction()
        self.estacionOrigen = estacionOrigen
        self.estacionDestino = estacionDestino
        self.pasoAccesoEntrada = False
        self.pasoAccesoSalida = False
        self.salioVagon = False
        self.entroVagon = False

    def get_position(self):
        return self.pos
    def set_position(self, pos):
        self.pos = pos
    
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
        indicePuertas  = math.floor(posPasajero[0]/LARGO_ANDEN)
        puertas = modelo.getPuertas(indicePuertas)
        for puerta in puertas:
            distancias.append( math.pow( posPasajero[0] - puerta.get_pos()[0], 2) + math.pow(posPasajero[1] - puerta.get_pos()[1], 2) )
        return puertas[ distancias.index(min(distancias)) ] 

    def elegirPuertaRandom(self,modelo, posPasajero):
        indicePuertas  = math.floor(posPasajero[0]/LARGO_ANDEN)
        puertas = modelo.getPuertas(indicePuertas)
        index = self.random.randint(0,(len(puertas)-1))
        return puertas[index] 

    

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
            if type(accesoDestino) is Puerta:
                distancias.append( math.pow( destinoSiguiente[0] - accesoDestino.get_pos()[0], 2) + math.pow(destinoSiguiente[1] - accesoDestino.get_pos()[1], 2) )
            else:
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
        id_anden = math.floor(self.pos[0]/LARGO_ANDEN)
        # print("IDANDEN", id_anden) 

        if( int(id_anden) == int(self.estacionDestino)):
            # print("ANDEN ",id_anden,": DESTINO  : ", self.estacionDestino)
            self.direccion = False
        if self.pos in self.model.posPuertas[id_anden] and self.direccion and not self.entroVagon:
            self.entroVagon = True
            # self.model.pasajerosEntraronTren+=1
        elif self.pos in self.model.posPuertas[id_anden] and not self.direccion and not self.salioVagon:
            self.salioVagon = True
            # self.model.pasajerosSalieronTren+=1
        elif self.pos in self.model.posAccesosEntrada and self.direccion and not self.pasoAccesoEntrada:
            self.pasoAccesoEntrada = True
            self.model.pasajerosEntraronAccesos+=1
        elif self.pos in self.model.posAccesosSalida and not self.direccion and not self.pasoAccesoEntrada:
            self.pasoAccesoSalida = True
            self.model.pasajerosSalieronAccesos+=1
        if self.pos[0] == POSX_ORIGEN or self.pos[0] == POSX_FINAL -1  or self.pos[1] == POSY_ORIGEN or self.pos[1] == POSY_FINAL -1:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
        
        # elif self.model.contador == TIMERCERRAR -1 and self.pos[1] < POSY_MURO_TREN +1 and not self.model.puertas[id_anden][0].cerrada:
        #     self.model.schedule.remove(self)
        #     self.model.grid.remove_agent(self)
        # elif self.model.contador == TIMERCERRAR -1 and self.pos[1] == POSY_MURO_TREN +1 and self.direccion and not self.model.puertas[id_anden][0].cerrada:
        #     self.model.schedule.remove(self)
        #     self.model.grid.remove_agent(self)
            
        else:
            #Fuera de los accesos
            if self.pos[1] > POSY_MURO_ENTRADA and self.direccion == True: 
                accesoDestino = self.elegirAcceso(self.model, self.pos, self.direccion)
                destinosPosibles = self.obtenerDestinosPosibles(accesoDestino, self.direccion)
                destino = self.obtenerDestino(destinosPosibles,accesoDestino)
            #Dentro de la estacion direccion puerta
            elif self.pos[1] <= POSY_MURO_ENTRADA and self.pos[1] > POSY_MURO_TREN and self.direccion == True: 
                puertaDestino = self.elegirPuerta(self.model, self.pos)
                destinosPosibles = self.obtenerDestinosPosiblesPuertas(puertaDestino)
                destino = self.obtenerDestino(destinosPosibles,puertaDestino)
                
                if puertaDestino == destino:
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
                puertaDestino = self.elegirPuerta(self.model, self.pos)
                destinosPosibles = self.obtenerDestinosPosiblesPuertas(puertaDestino)
                destino = self.obtenerDestino(destinosPosibles,puertaDestino)
                if puertaDestino == destino:
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
            puertas_r = self.model.puertas[id_anden]
            check = [x for x in puertas_r if x.get_pos() == destino and x.cerrada]
            if check == []:
                self.model.grid.move_agent(self,destino)

class Tren(Agent):
    def __init__(self, model, pos, id, colorRuta):
        super().__init__(self,model)
        self.servicio = True
        self.capacidadUsuarios = 0
        self.cantidadUsuarios = 0
        self.colorRuta = colorRuta
        self.pasajeros = []
        self.valorPuerta = False
        self.direccion = False
        self.pos = pos
        self.estacionActual = 0
        self.estacionSiguiente = 0
        self.estacionObjetivo = 0
        self.contador = 0
        self.id = id
    
    def step(self):
        print("T",self.id,": Vagon ID  : ", self.id)
        print("T",self.id,": Posicion  : ", self.pos)
        self.contador +=1
        anden  = math.floor(self.pos[0]/LARGO_ANDEN)
        puertas = self.model.puertas[anden]
        # print("Puertas", anden)

        #Abrir Puertas Tomar pasajeros
        if(self.contador == TIMERABRIR) and (LISTA_ESTACIONES[anden][3]%2) == self.colorRuta: #and la estacion es la suya
            # print("T",self.id,": OpenDoor  : ",anden)
            for puerta_o in puertas:
                # print("T",self.id,": O<nDoor  : ",puerta_o.pos)
                puerta_o.cerrada =  False
            # for mod in self.model.puertas:
            #     for pu in mod:
            #         print("X", pu.cerrada)
            
        # Cerrar Puertas
        elif self.contador == TIMERCERRAR:
            print("T",self.id,": CloseDoor : ",anden)
            for puerta_c in puertas:
                puerta_c.cerrada =  True
            # for mod in self.model.puertas:
            #     for pu in mod:
            #         print("X", pu.cerrada)

            #Captar pasajeros
            self.pasajeros = self.obtenerPasajerosEnRango((self.pos[0]+2-50),(self.pos[0]+2), 0,POSY_MURO_TREN)
            print("T",self.id,": Pasajeros : ",len(self.pasajeros))
            print("T",self.id,": limpieza  : ", (self.pos[0]+2-50) , (self.pos[0]+2))

            #Mover tren
            desplaNuevaEstacion = self.pos[0] + LARGO_ANDEN
            destino = (desplaNuevaEstacion, self.pos[1])
            ocup_andensiguiente = self.model.grid.get_neighbors( destino,moore=True, include_center=True,radius=0)
            tren_andensiguiente = [x for x in ocup_andensiguiente if type(x) is Tren]
            print(tren_andensiguiente)

            # verificar que no haya tren en el siguiente paso
            if destino[0] < POSX_FINAL and len(tren_andensiguiente) == 0 : 
                # Remover tren y pasajeros de la grilla
                total = self.moverPasajerosEnRango((self.pos[0]-LARGO_ANDEN+2), (self.pos[0]+2), 0, POSY_MURO_TREN)
                print("LEER x0: ",(self.pos[0]-LARGO_ANDEN+2),"x1: ",(self.pos[0]+2),"y0: ",0,"y1: ",POSY_MURO_TREN)
                self.model.grid.move_agent(self,destino)
                print("T",self.id,": cantidad  : ",len(total))
            else: 
                print("T",self.id,": Fin Viaje . ")
            self.contador = 0 
        
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)

    def obtenerPasajerosEnRango(self,xinicial,xfinal, yinicial,yfinal):
        totalPasajeros = []
        for x in range(xinicial,xfinal + 1):
            for y in range(yinicial,yfinal):
                pos = (x,y)
                pasajeros = self.model.grid.get_neighbors( pos,moore=True, include_center=True,radius=0)
                pasajeros = [x for x in pasajeros if type(x) is Pasajero and x.direccion == True]
                self.pasajeros += pasajeros
                if len(pasajeros) > 0:
                    totalPasajeros = totalPasajeros + pasajeros
        return totalPasajeros
    
    def moverPasajerosEnRango(self,xinicial, xfinal, yinicial, yfinal):
        totalPasajeros = []
        for x in range(xinicial,xfinal + 1):
            for y in range(yinicial,yfinal):
                pos = (x,y)
                pasajeros = self.model.grid.get_neighbors( pos,moore=True, include_center=True,radius=0)
                pasajeros = [x for x in pasajeros if type(x) is Pasajero]
                
                for pa in pasajeros:
                    # print("PI",pa.get_position())
                    x_dp = (pa.get_position()[0]+LARGO_ANDEN)
                    y_dp = pa.get_position()[1]
                    destino_p = (x_dp, y_dp)
                    # print("PF",destino_p)
                    self.model.grid.move_agent(pa,destino_p)
                    # pa.set_position(destino_p)
                    # print("PR",pa.get_position()) 
                if len(pasajeros) > 0:
                    totalPasajeros = totalPasajeros + pasajeros
        return totalPasajeros
    
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


