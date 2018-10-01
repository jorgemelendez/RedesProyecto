import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress
from random import randrange

from socket import error as SocketError
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
			if randrange(10) > 1:
				serverSocket.sendto((1).to_bytes(1, byteorder='big'), (clientAddress[0], clientAddress[1]))
				print(message)

	def procRecibeMsg(self, ip, puerto):
		#self.lockMensajesRecibidos.acquire()
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		serverSocket.bind((ip, puerto))
		self.recibeMensajes(serverSocket)
		#self.lockMensajesRecibidos.release()


if __name__ == '__main__':
	mensajesRecibidos= MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()
	receptorUDP = ReceptorUDP(mensajesRecibidos, tablaAlcanzabilidad)
	proceso_receptorUDP = threading.Thread(target=receptorUDP.procRecibeMsg, args=("10.1.137.57",5000,))
	proceso_receptorUDP.start()