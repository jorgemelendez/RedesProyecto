from CSVTopologia import *
from ArmarMensajes import *
import threading
import threading
import socket
import os
import sys

class TablaVecinos:

	#Construtor
	def __init__(self, bitacora):
		self.bitacora = bitacora
		self.parser = dict()
		self.lockParser = threading.Lock()
		self.diccVecinos = dict() #El formato va a ser:  key=(ip,mascara,puerto) valor=(costo,bitActivo)
		self.lockDiccVecinos = threading.Lock()

	#Metodo para ingresar los vecinos que indica el ServerVecinos
	# guarda los vecinos en un diccionario
	#mensajeVecinos: mensaje enviado por el ServerVecinos de cuales son mis vecinos
	def ingresarVecinos(self, mensajeVecinos):
		largo = int(len(mensajeVecinos) / 10)
		i = 0
		self.lockDiccVecinos.acquire()
		self.lockParser.acquire()
		while i < largo:
			ipi = bytesToIp(mensajeVecinos[0+i*10 : 4+i*10]) #0 - 3 --> IP, 4 bytes
			masci = bytesToInt(mensajeVecinos[4+i*10 : 5+i*10])#4 --> Mascara, 1 byte
			puertoi = bytesToInt(mensajeVecinos[5+i*10 : 7+i*10])#5 - 6 --> Puerto, 3 bytes
			distaciai = bytesToInt(mensajeVecinos[7+i*10 : 10+i*10])#7 --> Distancia, 3 bytes
			llave = ipi,masci,puertoi # la llave del diccionaroi es la (Ip, Mascara, Puerto)
			valor = distaciai, False #El valor va a ser (distancia,bitActivo)
			self.diccVecinos[llave] = valor
			self.parser[(ipi,puertoi)] = llave
			self.bitacora.escribir("TablaVecinos: " + "Se annadio el vecino " + str(llave) + " con distancia " + str(distaciai) + " y el bit como " + str(False))
			i = i + 1
		self.lockParser.release()
		self.lockDiccVecinos.release()

	#Funcion que retorna la distancia que existe hacia un vecino
	# retorna nulo si no existe ese como vecino
	#ip: ip del vecino
	#mascara: mascara del vecino
	#puerto: puerto del vecino
	def obtenerDistancia(self, ip, mascara, puerto):
		llave = ip, mascara, puerto
		self.lockDiccVecinos.acquire()
		valor = self.diccVecinos[llave]
		self.lockDiccVecinos.release()
		return valor[0] #En la tupla el primer valor es la distancia 

	#Metodo para modificar la distancia hacia un vecino
	# debe estar seguro que ese es un vecino suyo
	#ip: ip del vecino
	#mascara: mascara del vecino
	#puerto: puerto del vecino
	#distancia: nueva distancia hacia el vecino
	def modificarDistancia(self, ip, mascara, puerto, distancia):
		llave = ip, mascara, puerto
		self.lockDiccVecinos.acquire()
		self.diccVecinos[llave] = distancia, self.diccVecinos[llave][1] #Se mete la nueva distancia y se deja el valor antiguo del bitActivo
		self.lockDiccVecinos.release()
		self.bitacora.escribir("TablaVecinos: " + "Se modifico la distancia del vecino " + str(llave) + " por " + str(distancia))

	#Funcion que retorna si el vecino se encientra como activo o no en la tabla de vecinos
	# retorna True si el vecino esta activo, False en caso contrario
	#ip: ip del vecino
	#mascara: mascara del vecino
	#puerto: puerto del vecino
	def obtenerBitActivo(self, ip, mascara, puerto):
		llave = ip, mascara, puerto
		self.lockDiccVecinos.acquire()
		valor = self.diccVecinos[llave]
		self.lockDiccVecinos.release()
		return valor[1] #En la tupla el segundo valor es el bitActivo del vecino 

	#Metodo para modificar el BitActivo del vecino
	# debe estar seguro que ese es un vecino suyo
	#ip: ip del vecino
	#mascara: mascara del vecino
	#puerto: puerto del vecino
	#bitActivo: nueva bitActivo del vecino
	def modificarBitActivo(self, ip, mascara, puerto, bitActivo):
		llave = ip, mascara, puerto
		#self.bitacora.escribir("VOY A PEDIR EL CANDADO")
		self.lockDiccVecinos.acquire()
		#self.bitacora.escribir("CANDADO AGARRADO")
		self.diccVecinos[llave] = self.diccVecinos[llave][0], bitActivo #Se mete la nueva distancia y se deja el valor antiguo del bitActivo
		self.lockDiccVecinos.release()
		#self.bitacora.escribir("CANDADO LIBERADO")
		self.bitacora.escribir("TablaVecinos: " + "Se modifico el bitActivo del vecino " + str(llave) + " por " + str(bitActivo))

	#Metodo que recorre el diccionario e imprime la tabla
	# Formato de la tabla es (ip mascara puerto distancia bitActivo)
	def imprimirTablaVecinos(self):
		self.lockDiccVecinos.acquire()
		llaves = self.diccVecinos.keys()
		for x in llaves:
			valor = self.diccVecinos[x]
			print( str(x) + " " + str(valor[0]) + " " + str(valor[1]) )
		self.lockDiccVecinos.release()

	#Funcion que retornar los vecinos
	def obtenerVecinos(self):
		self.lockDiccVecinos.acquire()
		llaves = self.diccVecinos.keys()
		self.lockDiccVecinos.release()
		return llaves

	#Metodo que retorna una lista de los vecinos que se encuentran activos en la tabla de vecinos
	# Formato de la lista es (ip mascara puerto)
	def obtenerVecinosActivos(self):
		self.lockDiccVecinos.acquire()
		llaves = self.diccVecinos.keys()
		vecinosActivos = list()
		for x in llaves:
			valor = self.diccVecinos[x]
			if valor[1]:
				vecinosActivos.append(x)
		self.lockDiccVecinos.release()
		return vecinosActivos

	#Metodo que retorna una lista de los vecinos que se encuentran activos
	# Formato de la lista es (ip mascara puerto distancia)
	def obtenerVecinosActivosConDistancia(self):
		self.lockDiccVecinos.acquire()
		llaves = self.diccVecinos.keys()
		vecinosActivos = list()
		for x in llaves:
			valor = self.diccVecinos[x]
			if valor[1]:
				vecinosActivos.append((x[0],x[1],x[2],valor[0]))
		self.lockDiccVecinos.release()
		return vecinosActivos

	#Funcion encargada de retornar (ip,mascara,puerto) dado (ip,puerto)
	#nodo: tupla (ip, puerto)
	def obtenerKey(self, nodo):
		self.lockParser.acquire()
		key = self.parser.get(nodo)
		self.lockParser.release()
		return key

	def existeVecinoActivo(self, key):
		self.lockDiccVecinos.acquire()
		valor = self.diccVecinos[key]
		self.lockDiccVecinos.release()
		if valor == None:#Caso donde no es mi vecino
			return False
		else:
			if valor[1]:#Caso esta activo
				return True
			else:#Caso no esta activo
				return False