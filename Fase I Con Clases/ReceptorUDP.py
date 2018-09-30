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

	def leerMensaje(self):
		#print('Ingrese la cantidad de tuplas que quiere enviar:')
		entradas = 0
		leerCantTuplas = True
		while leerCantTuplas:
			lectura = input( "Ingrese la cantidad de tuplas: " )
			try:
				entradas = int(lectura)
				leerCantTuplas = False
			except ValueError as e:
				print("Cantidad de tuplas invalido")
				leerCantTuplas = True
		
		vectorBytes = bytearray((entradas).to_bytes(2, byteorder='big'))
		i = 0
		
		while i < entradas:
			#print('Ingrese la tupla:')
			leer = True
			while leer:
				tupla = input("Ingrese una tupla(ip mascara puerto): ")
				tuplaDividida = tupla.split()# tupla.replace(" ", "/",1)
				if len(tuplaDividida) == 3 :
					ipPrueba = tuplaDividida[0] + "/" + tuplaDividida[1]
					try:
						n = ipaddress.ip_network(ipPrueba) 
					except ValueError as e:
						print ("Ip o mascara no valida")
						leer = True
					else:
						leer = False
						try:
							costo = int(tuplaDividida[2]) 
						except ValueError as e:
							print ("Costo no valido")
							leer = True
						else:
							if costo > 0 and costo < 65536:
								leer = False
							else:
								print ("Costo no valido")
								leer = True
				else:
					print ("Faltan valores")

			vectorBytes += self.tuplaToBytes(tupla)
			i = i + 1
			#print('\n')
		return vectorBytes