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

class EmisorUDP:

	def __init__(self, nodoId, mensajesRecibidos, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo):
		#self.mensajesRecibidos = mensajesRecibidos
		self.nodoId = nodoId
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo
		
	def tuplaToBytes(self,tupla):
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
				tupla = input("Ingrese una tupla(ip mascara costo): ")
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

	def envioMensajeUDP(self):
		serverNameS = input('Digite la ip del destinatario: ')
		ipPrueba = serverNameS + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			lecturaPuerto = input('Digite el puerto del destinatario: ')
			try:
				serverPortS = int(lecturaPuerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if serverPortS < 0 or serverPortS > 65535:
					print ("Puerto no valido")
				else:
					message = self.leerMensaje()
					self.lockSocketNodo.acquire()
					self.socketNodo.sendto(message, (serverNameS, serverPortS))
					self.lockSocketNodo.release()

	#Metodo que envia el mensaje de suicidio a los vecinos
	def borrarme(self):
		mensajeAvisoMuerte = bytearray()
		mensajeAvisoMuerte += intToBytes(4,1)#Tipo de mensaje es 4
		mensajeAvisoMuerte += intToBytes(24,1) #Se pone la mascara en el mensaje de solicitudes

		vecinos = self.tablaVecinos.obtenerVecinos()
		for x in vecinos:
			if self.tablaVecinos.obtenerBitActivo(x[0], x[1], x[2]) :
				self.lockSocketNodo.acquire()
				self.socketNodo.sendto( mensajeAvisoMuerte, (x[0], x[2]) )
				self.lockSocketNodo.release()
			else:
				print(str(x) + " vecino no activo ELIMINAR MENSAJE")

	def despligueMenuUDP(self):

		bandera = True
		while bandera == True:
			print( "Soy el nodo " + str(self.nodoId) )
			print('Menu principal del modulo de Red UDP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Ver mensajes recibidos. \n'
					'\t3. Imprimir tabla de alcanzabilidad.\n'
					'\t4. Imprimir tabla de vecinos.\n'
					'\t5. Cerrar servidor de mensajes.')
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				self.envioMensajeUDP()
			elif taskUsuario == '2':
				print("\n\n")
				print('Opcion deshabilitada')
				#print('Mensajes recibidos:')
				#self.mensajesRecibidos.imprimirMensajes()
				print("\n\n")
			elif taskUsuario == '3':
				print("\n\n")
				print('Tabla de alcanzabilidad:')
				self.tablaAlcanzabilidad.imprimirTabla()
				print("\n\n")
			elif taskUsuario == '4':
				print("\n\n")
				print('Tabla de vecinos:')
				self.tablaVecinos.imprimirTablaVecinos()
				print("\n\n")
			elif taskUsuario == '5':
				bandera = False
				self.borrarme()
				print('Salida.')
				os._exit(1)

			else:
				print('Ingrese opcion valida.')