import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress
import time
from socket import error as SocketError
from ArmarMensajes import *
from TablaAlcanzabilidad import *
from TablaVecinos import *

class HiloVerificacionVivo:

	#Constructor
	#tablaAlcanzabilidad: Tabla de alcanzabilidad para construir el mensaje
	#tablaVecinos: Tabla de vecinos para saber a quien enviarselos
	#socketNodo: socket del nodo para enviar la tabla
	#lockSocketNodo: lock para utilizar el socket
	def __init__(self, nodoId, vecino, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo, bitacora):
		self.bitacora = bitacora
		self.nodoId = nodoId
		self.vecino = vecino
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo
		self.buzon = list()
		self.lockBuzon = threading.Lock()

	#Metodo que ingresa un mensaje al buzon
	def meterBuzon(self, mensaje):
		self.lockBuzon.acquire()
		self.buzon.append(mensaje)
		self.lockBuzon.release()

	#Metodo llama a limpiar la tabla de alcanzabilidad
	def eventoMurioVecino(self):
		self.tablaVecinos.modificarBitActivo(self.vecino[0], self.vecino[1], self.vecino[2], False)
		vecinosActivosConDistancia = self.tablaVecinos.obtenerVecinosActivosConDistancia()
		self.tablaAlcanzabilidad.limpiarPonerVecinosActivos(vecinosActivosConDistancia)

	#Metodo que es el ciclo de envi mensaje para ver si esta vivo cada 30 segundos
	def iniciarCiclo(self):
		mensaje = bytearray()
		mensaje += intToBytes(32,1)#Tipos de mensaje es 32, verificacion de vivo
		mensaje += intToBytes(self.nodoId[1],1)#Se añade mi mascara
		intento = 0
		murioNodo = False
		while murioNodo == False:
			salir = False
			time.sleep(10)
			while salir == False:
				self.lockSocketNodo.acquire()
				self.socketNodo.sendto(mensaje, (self.vecino[0], self.vecino[2]))
				#print("Envie pregunta de vivo a " + str(self.vecino))
				self.lockSocketNodo.release()
				time.sleep(1)
				self.lockBuzon.acquire()
				haymensaje = len(self.buzon)
				self.lockBuzon.release()
				if haymensaje == 0:
					time.sleep(1)
					self.lockBuzon.acquire()
					haymensaje = len(self.buzon)
					self.lockBuzon.release()
					if haymensaje == 0:
						intento = intento + 1
						if intento == 5:
							#print("Murio el vecino " + str(self.vecino))
							self.bitacora.escribir("Murio el vecino " + str(self.vecino))
							self.eventoMurioVecino()
							murioNodo = True
							salir = True
					else:
						intento = 0
						salir = True
						self.lockBuzon.acquire()
						mensajeRecibido = self.buzon.pop()
						self.lockBuzon.release()
				else:
					intento = 0
					salir = True
					self.lockBuzon.acquire()
					mensajeRecibido = self.buzon.pop()
					self.lockBuzon.release()