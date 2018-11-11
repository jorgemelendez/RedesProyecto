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

	#Constructor
	#nodoId: id del nodo, tupla (ip, mascara, puerto)
	#tablaAlcanzabilidad: tabla de alcanzabilidad del nodo
	#tablaVecinos: tabla de vecinos del nodo
	#socketNodo: sockect del nodo
	#lockSocketNodo: lock del socket del nodo
	def __init__(self, nodoId, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo):
		self.nodoId = nodoId
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo

	#Metodo para responder a vecino que si estoy vivo
	#vecino: tupla que es (ip, puerto)
	#mensaje: mascara del vecino
	def responderVivo(self, vecino, mensaje):
		mensajeRespContacto = bytearray()
		mensajeRespContacto += intToBytes(2,1)#Tipo de mensaje es 1
		mensajeRespContacto += intToBytes(self.nodoId[1],1) #Se pone la mascara en el mensaje de solicitudes
		mascara = bytesToInt(mensaje[1:2])
		estadoVecino = self.tablaVecinos.obtenerBitActivo(vecino[0], mascara, vecino[1])
		distancia = self.tablaVecinos.obtenerDistancia(vecino[0], mascara, vecino[1])
		tuplaVecino = vecino[0], mascara, vecino[1]
		self.tablaAlcanzabilidad.annadirAlcanzable( tuplaVecino, distancia, tuplaVecino )
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
	#mensaje: mascara del vecino
	def respondieronVivo(self, vecino, mensaje):
		mascara = bytesToInt(mensaje[1:2])
		print("Este tipo de mensajes(resp Vivo) no deberian de llegar estando dentro de ReceptorUDP")

	#Metodo para desactivar vecino en la tabla vecinos y sacar las entradas a las que se llevaban mediante este
	#vecino: tupla que es (ip. puerto)
	#mensaje: mascara del vecino
	def murioVecino(self, vecino, mensaje):
		mascara = bytesToInt(mensaje[1:2])
		self.tablaVecinos.modificarBitActivo(vecino[0], mascara, vecino[1], False) #Se pone como un vecino no activo
		self.tablaAlcanzabilidad.borrarAtravez(vecino[0], mascara, vecino[1]) #Se borran las entradas con las que se iban atravez de ese nodo

	#Metodo que procesa un mensaje de actualizacion de tabla
	#vecino: tupla que es (ip. puerto)
	#mensaje: mensaje recibido, viene la mascara en el segundo byte
	def mensajeActualizacionTabla(self, vecino, mensaje):
		mensajeQuitandoTipo = mensaje[2:]
		vecinoConMascara = vecino[0], bytesToInt( mensaje[1:2] ), vecino[1]
		distanciaVecino = self.tablaVecinos.obtenerDistancia(vecino[0], bytesToInt( mensaje[1:2] ), vecino[1])
		self.tablaAlcanzabilidad.actualizarTabla(mensajeQuitandoTipo, vecinoConMascara, distanciaVecino)

	#Metodo encargado de recibir los mensajes que le envian al nodo
	def recibeMensajes(self):
		while 1:
			message, clientAddress = self.socketNodo.recvfrom(2048)
			tipoMensaje = bytesToInt(message[0:1])
			if tipoMensaje == 1:
				self.responderVivo(clientAddress, message)
			elif tipoMensaje == 2:#Creo que este caso no tiene sentido aqui, pero por si llegara uno, para decir que esta fuera de lugar
				self.respondieronVivo(clientAddress, message)
			elif tipoMensaje == 4:
				self.murioVecino(clientAddress, message)
			elif tipoMensaje == 8:
				self.mensajeActualizacionTabla(clientAddress, message)
			else:
				print("Llego mensaje con tipo desconocido")