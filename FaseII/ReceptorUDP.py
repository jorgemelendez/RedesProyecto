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

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad

	def recibeMensajes(self, serverSocket):
		while 1:
			message, clientAddress = serverSocket.recvfrom(2048)
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

	def procRecibeMsg(self, ip, puerto):
		#self.lockMensajesRecibidos.acquire()
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		serverSocket.bind((ip, puerto))
		self.recibeMensajes(serverSocket)
		#self.lockMensajesRecibidos.release()