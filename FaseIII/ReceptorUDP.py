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
from ArmarMensajes import *


class ReceptorUDP:
	#mensajesRecibidos = MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo):
		#self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo

	#Metodo para responder a vecino que si estoy vivo
	#vecino: tupla que es (ip, puerto)
	#mascara: mascara del vecino
	def responderVivo(self, vecino, mensaje):
		mensajeRespContacto = bytearray()
		mensajeRespContacto += intToBytes(2,1)#Tipo de mensaje es 1
		mensajeRespContacto += intToBytes(24,1) #Se pone la mascara en el mensaje de solicitudes
		mascara = bytesToInt(mensaje[1:2])
		estadoVecino = self.tablaVecinos.obtenerBitActivo(vecino[0], mascara, vecino[1])
		if estadoVecino == None:
			print(str(vecino[0]) + " " + str(mascara) + " " + str(vecino[0]) + " no es uno de mis vecinos")
		elif estadoVecino == True:
			print(str(vecino[0]) + " " + str(mascara) + " " + str(vecino[0]) + " ya estaba como vecino activo")
		else:
			self.tablaVecinos.modificarBitActivo(vecino[0], mascara, vecino[1], True)
			self.lockSocketNodo.acquire()
			self.socketNodo.sendto(mensajeRespContacto, vecino)
			self.lockSocketNodo.release()

	#Metodo para activar vecino en la tabla vecinos, y meterlo en la tabla de vecinos
	#vecino: tupla que es (ip. puerto)
	#mascara: mascara del vecino
	def respondieronVivo(self, vecino, mensaje):
		mascara = bytesToInt(mensaje[1:2])
		print("Este tipo de mensajes(resp Vivo) no deberian de llegar estando dentro de ReceptorUDP")

	#Metodo para activar vecino en la tabla vecinos, y meterlo en la tabla de vecinos
	#vecino: tupla que es (ip. puerto)
	#mascara: mascara del vecino
	def murioVecino(self, vecino, mensaje):
		mascara = bytesToInt(mensaje[1:2])
		self.tablaVecinos.modificarBitActivo(vecino[0], mascara, vecino[1], False) #Se pone como un vecino no activo
		self.tablaAlcanzabilidad.borrarAtravez(vecino[0], mascara, vecino[1]) #Se borran las entradas con las que se iban atravez de ese nodo

	def recibeMensajes(self):
		while 1:
			#self.lockSocketNodo.acquire()
			message, clientAddress = self.socketNodo.recvfrom(2048)
			#self.lockSocketNodo.release()
			#mensaje = Mensaje(clientAddress[0],clientAddress[1], message)
			tipoMensaje = bytesToInt(message[0:1])
			if tipoMensaje == 1:
				self.responderVivo(clientAddress, message)
			elif tipoMensaje == 2:#Creo que este caso no tiene sentido aqui
				self.respondieronVivo(clientAddress, message)
			elif tipoMensaje == 4:
				self.murioVecino(clientAddress, message)

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
