import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from MensajesRecibidos import *
from TablaAlcanzabilidad import *
from ReceptorUDP import *
from EmisorUDP import *

class NodoUDP:

	def __init__(self, ip, puerto):
		self.mensajesRecibidos = MensajesRecibidos()
		self.tablaAlcanzabilidad = TablaAlcanzabilidad()
		#self.tablaVecinos = TablaVecinos()
		self.socketNodo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketNodo.bind((ip, puerto))
		self.lockSocketNodo = threading.Lock()

	#Retorna 1 si se pudo comunicar con el servidor de vecinos
	#Retorna 0 si no se pudo comunicar con el servidor de vecinos
	def pedirVecinos(self):
		mensajeSolicitudVecinos = bytearray()
		mensajeSolicitudVecinos += intToBytes(24,1) #Se pone la mascara en el mensaje de solicituds
		banderaParada = False

		self.socketNodo.settimeout(0.5)
		intento = 1
		while not(banderaParada):
			self.lockSocketNodo.acquire()
			self.socketNodo.sendto(mensajeSolicitudVecinos, ("192.168.100.17", 5000))
			self.lockSocketNodo.release()
			vecinos = bytearray()
			try:
				vecinos, serverAddress = self.socketNodo.recvfrom(2048)
			except socket.timeout:
				intento = intento + 1
				if intento == 10:# ver si se aumenta mas
					print("El servidor no esta activo")
					banderaParada = True
			else:
				print(vecinos)
				banderaParada = True

		self.socketNodo.settimeout(None)
		if intento == 10:
			return 0
		else:
			return 1

	def iniciarNodoUDP(self):
		llenaronVecinos = self.pedirVecinos()
		if llenaronVecinos == 1:
			receptorUDP = ReceptorUDP(self.mensajesRecibidos, self.tablaAlcanzabilidad, self.socketNodo, self.lockSocketNodo)
			proceso_receptorUDP = threading.Thread(target=receptorUDP.recibeMensajes, args=())
			proceso_receptorUDP.start()

			emisorUDP = EmisorUDP(self.mensajesRecibidos, self.tablaAlcanzabilidad, self.socketNodo, self.lockSocketNodo)
			proceso_emisorUDP = threading.Thread(target=emisorUDP.despligueMenuUDP, args=())
			proceso_emisorUDP.start()
		else:
			print("Error al tratar de comunicarse con el ServerVecinos")

		