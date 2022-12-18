import numpy as np
import csv 

with open('viajesCompleto.csv', 'r') as f:
    data = list(csv.reader(f, delimiter=","))

dataarray = np.array(data)
dataarray = np.delete(dataarray,(0), axis = 0)
dataarray[dataarray[:,2].argsort()]

tini= dataarray[0][2].split(':')
tfin= dataarray[-1][2].split(':')



ini = int(tini[0])*60*60 + int(tini[1])*60 + int(tini[2])
fin = int(tfin[0])*60*60 + int(tfin[1])*60 + int(tfin[2])

ticks = int((fin-ini)/15)

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
