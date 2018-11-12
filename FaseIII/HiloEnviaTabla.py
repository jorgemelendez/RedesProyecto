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

class HiloEnviaTabla:

	#Constructor
	#tablaAlcanzabilidad: Tabla de alcanzabilidad para construir el mensaje
	#tablaVecinos: Tabla de vecinos para saber a quien enviarselos
	#socketNodo: socket del nodo para enviar la tabla
	#lockSocketNodo: lock para utilizar el socket
	def __init__(self, nodoId, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo, bitacora):
		self.bitacora = bitacora
		self.nodoId = nodoId
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo

	#Metodo encargado de crear el mensaje que se va a enviar a un vecino
	#vecino: tupla (ip, mascara, puerto) del vecino
	#tablaEnrutamiento: tabla de alcanzabilidad que se le pidio a TablaAlcanzabilidad
	def construirMensaje(self, vecino, tablaEnrutamiento):
		mensaje = bytearray()
		mensaje += intToBytes(8,1)#Tipos de mensaje es 8, actualizacion de la tabla
		mensaje += intToBytes(self.nodoId[1],1)#Se annade la mascara en el mensaje
		cantidaTuplasEnviar = (len(tablaEnrutamiento) - 1)# -1 porque no se manda la tupla del nodo que estoy contactando
		mensaje += intToBytes(cantidaTuplasEnviar,2)
		for x in tablaEnrutamiento: #Cada x tiene la forma (ip, mascara, puerto, distancia)
			if (x[0],x[1],x[2]) != vecino:
				mensaje += ipToBytes(x[0])#Mete la ip como 4 bytes
				mensaje += intToBytes(x[1],1)#Mete la mascara como 1 byte
				mensaje += intToBytes(x[2],2)#Mete el puerto como 2 bytes
				mensaje += intToBytes(x[3],3)#Mete la distancia como 3 bytes
		return mensaje

	#Metodo que se encarga de enviar los mensajes a todos sus vecinos
	def enviarTablaAVecinos(self):
		vecinos = self.tablaVecinos.obtenerVecinosActivos() #Vecinos activos
		tabla = self.tablaAlcanzabilidad.obtenerTabla() #Tabla de alcanzabilidad completa
		for x in vecinos:
			mensajeTablaParaVecino = self.construirMensaje(x, tabla)
			self.lockSocketNodo.acquire()
			self.socketNodo.sendto( mensajeTablaParaVecino, (x[0], x[2]) )
			self.lockSocketNodo.release()
			self.bitacora.escribir("HiloEnviaTabla: " + "Se envio la tabla de enrrutamiento al vecino " + str(x))

	#Metodo que es el ciclo de envio de tablas cada 30 segundos
	def iniciarCiclo(self):
		while True:
			self.enviarTablaAVecinos()
			time.sleep(5)