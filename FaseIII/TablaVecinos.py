from CSVTopologia import *
from ArmarMensajes import *
import threading
import threading
import socket
import os
import sys

class TablaVecinos:

	diccVecinos = dict()
	lockDiccVecinos = threading.Lock()

	#Constructor donde se pasa:
	# 	- El objeto de bytearray de los vecinos
	#	- Lock para actualizar el valor de vivo de las conexiones
	def __init__(self, objetoVecinos):
		self.lockDiccVecinos = threading.Lock()
		descomprimirVecinos(objetoVecinos)

	#Metodo que recibe el objetoVecinos que es el bytearray
	#	y el metodo se encarga de descomprimirlos y ponerlos
	#	dentro del diccionario
	def descomprimirVecinos(objetoVecinos):
		
		largo = len(objetoVecinos)
		while i < largo:
			ip1 	= bytesToIp(objetoVecinos[0:4])								#0 - 3 	--> IP
			masc1 	= int.from_bytes(objetoVecinos[4:5], byteorder='big')		#4 	   	--> Mascara
			puerto1 = int.from_bytes(objetoVecinos[5:7], byteorder='big')		#5 		--> Puerto			
			ip2 	= bytesToIp(objetoVecinos[0:4])								#6		--> 







