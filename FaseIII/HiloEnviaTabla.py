import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress
from socket import error as SocketError
from ArmarMensajes import *
from TablaAlcanzabilidad import *
from TablaVecinos import *

class HiloEnviaTabla:

	#Constructor
	#tablaAlcanzabilidad: Tabla de alcanzabilidad para construir el mensaje
	#tablaVecinos: Tabla de vecinos para saber a quien enviarselos
	#socketNodo: socket del nodo para enviar la tabla
	#lockSocketNodo: lock para utilizar el socket
	def __init__(self, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo):
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo

	#Metodo encargado de crear el mensaje que se va a enviar a un vecino
	#vecino: tupla (ip, mascara, puerto) del vecino
	#tablaEnrutamiento: tabla de alcanzabilidad que se le pidio a TablaAlcanzabilidad
	def construirMensaje(self, vecino, tablaEnrutamiento):
		mensaje = bytearray()
		cantidaTuplasEnviar = (len(tablaEnrutamiento) - 1)
		mensaje += intToBytes(cantidaTuplasEnviar,2)
		for x in tablaEnrutamiento:
			if (x[0],x[1],x[2]) != vecino:
				mensaje += ipToBytes(x[0])#Mete la ip como 4 bytes
				mensaje += intToBytes(x[1],1)#Mete la mascara como 1 byte
				mensaje += intToBytes(x[0],2)#Mete el puerto como 2 bytes
				mensaje += intToBytes(x[0],1)#Mete la distancia como 1 bytes

	#Metodo que se encarga de enviar los mensajes a todos sus vecinos
	def enviarTablaAVecinos(self):
		vecinos = self.tablaVecinos.obtenerVecinosActivos() #Vecinos activos
		tabla = self.tablaAlcanzabilidad.obtenerTabla() #Tabla de alcanzabilidad completa
		for x in vecinos:
			mensajeTablaParaVecino = self.construirMensaje(x, tabla)
			self.lockSocketNodo.acquire()
			self.socketNodo.sendto( mensajeTablaParaVecino, (x[0], x[2]) )
			self.lockSocketNodo.release()