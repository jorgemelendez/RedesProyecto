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
from TablaVecinos import *
from ReceptorUDP import *
from EmisorUDP import *
from HiloEnviaTabla import *

class NodoUDP:

	#Constructor
	#ip: ip de la maquina donde va a ser iniciado
	#puerto: puerto donde va a ser iniciado
	def __init__(self, ip, puerto):
		self.nodoId = ip, puerto
		self.mensajesRecibidos = MensajesRecibidos()
		self.tablaAlcanzabilidad = TablaAlcanzabilidad()
		self.tablaVecinos = TablaVecinos()
		self.socketNodo = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketNodo.bind((ip, puerto))
		self.lockSocketNodo = threading.Lock()

	#Funcion para pedir los vecinos al ServerVecinos
	#Retorna 1 si se pudo comunicar con el servidor de vecinos
	#Retorna 0 si no se pudo comunicar con el servidor de vecinos
	def pedirVecinos(self):
		mensajeSolicitudVecinos = bytearray()
		mensajeSolicitudVecinos += intToBytes(24,1) #Se pone la mascara en el mensaje de solicitudes
		banderaParada = False
		vecinos = bytearray()
		self.socketNodo.settimeout(1)
		intento = 1
		while not(banderaParada):
			self.lockSocketNodo.acquire()
			self.socketNodo.sendto(mensajeSolicitudVecinos, ("192.168.100.17", 5000))
			self.lockSocketNodo.release()
			try:
				vecinos, serverAddress = self.socketNodo.recvfrom(2048)
			except socket.timeout:
				intento = intento + 1
				if intento == 10:# ver si se aumenta mas
					print("El servidor no esta activo")
					banderaParada = True
			else:
				if serverAddress == ("192.168.100.17", 5000):
					#print(vecinos)
					banderaParada = True
		self.socketNodo.settimeout(None)
		if intento == 10:
			return 0
		else:
			self.tablaVecinos.ingresarVecinos(vecinos)
			return 1

	#Metodo para intentar contactar a los vecinos para ver si estan activos
	# envia un mensaje a los vecinos (3 intentos) y espera respuesta
	# actualiza el bitActivo del vecino en la tabla de vecinos
	# si el vecino contesta, lo annade a la tabla de alcanzabilidad,(para indicar directo usa la misma tupla en atravez)
	def contactarVecinos(self):
		mensajeContactoVecino = bytearray()
		mensajeContactoVecino += intToBytes(1,1)#Tipo de mensaje es 1
		mensajeContactoVecino += intToBytes(24,1) #Se pone la mascara en el mensaje de solicitudes
		#Se obtiene  los vecinos para intentar contactarlos
		vecinosTabla = self.tablaVecinos.obtenerVecinos()
		for x in vecinosTabla: #Cada x, es (ip, mascara, puerto)
			banderaParada = False
			vecinos = bytearray()
			self.socketNodo.settimeout(1) #Espera respuesta durante 1 segundo
			intento = 1
			print("Intentando contactar al vecino: " + str(x))
			while not(banderaParada): #While de intentos de contacto(maximo 3)
				self.lockSocketNodo.acquire()
				self.socketNodo.sendto(mensajeContactoVecino, (x[0], x[2]))
				self.lockSocketNodo.release()
				try:
					vecinos, serverAddress = self.socketNodo.recvfrom(2048)
				except socket.timeout:
					intento = intento + 1
					if intento == 3:# ver si se aumenta mas
						print("El vecino " + str(x) + " no esta activo")
						banderaParada = True
				else:
					if serverAddress == (x[0], x[2]):
						banderaParada = True
			self.socketNodo.settimeout(None)
			if intento == 3:
				self.tablaVecinos.modificarBitActivo(x[0], x[1], x[2], False)
			else:
				self.tablaVecinos.modificarBitActivo(x[0], x[1], x[2], True)
				distancia = self.tablaVecinos.obtenerDistancia(x[0], x[1], x[2])
				self.tablaAlcanzabilidad.annadirAlcanzable( x, distancia, x )

	#Metodo que da inico al nodo, pide los vecinos al ServerVecinos, intenta contactar a los vecinos 
	# manda a ejecutar un hilo receptor y el emisor(interfaz con usuario)
	def iniciarNodoUDP(self):
		llenaronVecinos = self.pedirVecinos()
		if llenaronVecinos == 1:
			#Se contactan los vecinos
			self.contactarVecinos()
			#Se crea el hilo de enviar tablas cada 30 segunodos
			hiloEnviaTabla = HiloEnviaTabla(self.tablaAlcanzabilidad, self.tablaVecinos, self.socketNodo, self.lockSocketNodo)
			proceso_hiloEnviaTabla = threading.Thread(target=hiloEnviaTabla.iniciarCiclo, args=())
			proceso_hiloEnviaTabla.start()
			#Se crea el hilo de recepcion de mensajes
			receptorUDP = ReceptorUDP(self.nodoId, self.mensajesRecibidos, self.tablaAlcanzabilidad, self.tablaVecinos, self.socketNodo, self.lockSocketNodo)
			proceso_receptorUDP = threading.Thread(target=receptorUDP.recibeMensajes, args=())
			proceso_receptorUDP.start()
			#Se crea el hilo emisor de mensajes (interfaz con el usuario)
			emisorUDP = EmisorUDP(self.nodoId, self.mensajesRecibidos, self.tablaAlcanzabilidad, self.tablaVecinos, self.socketNodo, self.lockSocketNodo)
			proceso_emisorUDP = threading.Thread(target=emisorUDP.despligueMenuUDP, args=())
			proceso_emisorUDP.start()
		else:
			print("Error al tratar de comunicarse con el ServerVecinos")

		