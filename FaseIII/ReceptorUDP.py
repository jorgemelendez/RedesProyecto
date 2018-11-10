import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from Mensaje import *
from MensajesRecibidos import *
from TablaAlcanzabilidad import *


class ReceptorUDP:
	mensajesRecibidos = MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo

	def recibeMensajes(self):
		while 1:
			#self.lockSocketNodo.acquire()
			message, clientAddress = self.socketNodo.recvfrom(2048)
			#self.lockSocketNodo.release()
			mensaje = Mensaje(clientAddress[0],clientAddress[1], message)

			cantTuplas = int(codecs.encode(message[0:2], 'hex_codec'))
			mensajeSalir = int.from_bytes( message[2:3], byteorder='big' )
			#Si el mensaje recibido es la palabra close se cierra la aplicacion
			if cantTuplas == 1 and len(message) == 3 and mensajeSalir == 0:
				print("Nodo aviso suicidio")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(clientAddress[0],clientAddress[1])
			else:
				self.mensajesRecibidos.guardarMensaje(mensaje)
				self.mensajesRecibidos.imprimirMensaje(mensaje)
				self.tablaAlcanzabilidad.actualizarTabla(mensaje)

	def tuplaToBytes(self, tupla):
		tupladiv = tupla.split(' ')
		numeroip = tupladiv[0]
		myip = numeroip.split('.')
		bytesmios = bytearray()
		for x in range(0, 4):
			ipnum = int(myip[x])
			bytesmios += (ipnum).to_bytes(1, byteorder='big')
		masc = int(tupladiv[1])
		bytesmios += (masc).to_bytes(1, byteorder='big')
		costo = int(tupladiv[2])
		bytesmios += (costo).to_bytes(3, byteorder='big')
		return bytesmios
