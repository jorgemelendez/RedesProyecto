from CSVTopologia import *
from ArmarMensajes import *
import threading
import threading
import socket
import os
import sys

class TablaVecinos:

	def __init__(self):
		self.diccVecinos = dict()
		self.lockDiccVecinos = threading.Lock()

	#Metodo que recibe el objetoVecinos que es el bytearray
	#	y el metodo se encarga de descomprimirlos y ponerlos
	#	dentro del diccionario
	def ingresarVecinos(self, objetoVecinos):
		largo = int(len(objetoVecinos) / 8)
		i = 0
		while i < largo:
			ipi = bytesToIp(objetoVecinos[0+i*8 : 4+i*8]) #0 - 3 --> IP
			masci = bytesToInt(objetoVecinos[4+i*8 : 5+i*8])#4 --> Mascara
			puertoi = bytesToInt(objetoVecinos[5+i*8 : 7+i*8])#5 - 6 --> Puerto
			distaciai = bytesToInt(objetoVecinos[7+i*8 : 8+i*8])#7 --> Distancia
			llave = ipi,masci,puertoi # la llave del diccionaroi es la (Ip, Mascara, Puerto)
			valor = distaciai, False #El valor va a ser (distancia,bitActivo)
			self.diccVecinos[llave] = valor
			i = i + 1

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
		self.lockDiccVecinos.acquire()
		self.diccVecinos[llave] = self.diccVecinos[llave][0], bitActivo #Se mete la nueva distancia y se deja el valor antiguo del bitActivo
		self.lockDiccVecinos.release()

	#Metodo que recorre el diccionario e imprime la tabla
	# Formato de la tabla es (ip mascara puerto distancia bitActivo)
	def imprimirTablaVecinos(self):
		llaves = self.diccVecinos.keys()
		for x in llaves:
			valor = self.diccVecinos[x]
			print( x[0] + " " + str(x[1]) + " " + str(x[2]) + " " + str(valor[0]) + " " + str(valor[1]) )

	#Funcion que retornar los vecinos
	def obtenerVecinos(self):
		self.lockDiccVecinos.acquire()
		llaves = self.diccVecinos.keys()
		self.lockDiccVecinos.release()
		return llaves

#if __name__ == '__main__':
#	tablaVecinos = TablaVecinos()
#	mensaje = bytearray()
#	mensaje =   ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(9000,2) + intToBytes(70,1)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(10000,2) + intToBytes(80,1)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(11000,2) + intToBytes(51,1)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(12000,2) + intToBytes(42,1)
#	
#	tablaVecinos.ingresarVecinos(mensaje)
#
#	tablaVecinos.imprimirTablaVecinos()
#
#
#	tablaVecinos.modificarDistancia("192.168.100.17", 24, 9000, 20)
#	tablaVecinos.modificarDistancia("192.168.100.17", 24, 10000, 30)
#	tablaVecinos.modificarDistancia("192.168.100.17", 24, 11000, 40)
#	tablaVecinos.modificarDistancia("192.168.100.17", 24, 12000, 50)
#
#	print("\n\n\n\n")
#
#	tablaVecinos.imprimirTablaVecinos()
#
#
#	tablaVecinos.modificarBitActivo("192.168.100.17", 24, 9000, True)
#	tablaVecinos.modificarBitActivo("192.168.100.17", 24, 10000, True)
#	tablaVecinos.modificarBitActivo("192.168.100.17", 24, 11000, True)
#	tablaVecinos.modificarBitActivo("192.168.100.17", 24, 12000, True)
#
#	print("\n\n\n\n")
#
#	tablaVecinos.imprimirTablaVecinos()