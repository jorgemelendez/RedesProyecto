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

	def responderACK(self, serverSocket, clientAddress):
		print("aqui")
		if randrange(10) > 1:
				serverSocket.sendto((1).to_bytes(1, byteorder='big'), (clientAddress[0], clientAddress[1]))
				print(clientAddress[0])
				print(clientAddress[1])
				#print(message)

	def recivir(self, serverSocket, numero):
		message, clientAddress = serverSocket.recvfrom(2048)
		self.responderACK(serverSocket, clientAddress)
		print(numero)
		print(message)

	def recibeMensajes(self, serverSocket):
		while 1:
			proceso_receptorUDP = threading.Thread(target=ReceptorUDP(None, None).recivir, args=(serverSocket,1,))
			proceso_receptorUDP.start()

			proceso_receptorUDP = threading.Thread(target=ReceptorUDP(None, None).recivir, args=(serverSocket,2,))
			proceso_receptorUDP.start()

			proceso_receptorUDP = threading.Thread(target=ReceptorUDP(None, None).recivir, args=(serverSocket,3,))
			proceso_receptorUDP.start()

			message, clientAddress = serverSocket.recvfrom(2048)
			#proceso_receptorUDP = threading.Thread(target=self.responderACK, args=(serverSocket,clientAddress,))
			#proceso_receptorUDP.start()
			#print("imprimi")
			

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
	proceso_receptorUDP = threading.Thread(target=receptorUDP.procRecibeMsg, args=("192.168.0.15",5000,))
	proceso_receptorUDP.start()