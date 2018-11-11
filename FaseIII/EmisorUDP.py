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

	#Constructor
	#nodoId: tupla id del nodo, (ip, mascara, puerto)
	#tablaAlcanzabilidad: tabla de alcanzabilidad del nodo
	#tablaVecinos: tabla de vecinos del nodo
	#socketNodo: socket del nodo
	#lockSocketNodo: lock del socket del nodo
	def __init__(self, nodoId, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo):
		self.nodoId = nodoId
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.tablaVecinos = tablaVecinos
		self.socketNodo = socketNodo
		self.lockSocketNodo = lockSocketNodo

	#Metodo encargado de enviar un mensaje por la red
	# falta hacer la lectura del mensaje que se quiere enviar
	def envioMensajeUDP(self):
		ipDigitada = input('Digite la ip del destinatario: ')
		ipPrueba = ipDigitada + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			lecturaMascara = input('Digite la mascara del destinatario: ')
			try:
				mascara = int(lecturaMascara)
			except ValueError as e:
				print ("Mascara no valida")
			else:
				if mascara < 2 or mascara > 30:
					print ("Mascara no valida, debe estar en [2,30]")
				else:
					lecturaMascara = input('Digite el puerto del destinatario: ')
					try:
						puerto = int(lecturaPuerto)
					except ValueError as e:
						print ("Puerto no valido")
					else:
						if puerto < 0 or puerto > 65535:
							print ("Puerto no valido")
						else:#Codigo para hacer y enviar el mensaje
							message = bytearray()
							self.lockSocketNodo.acquire()
							self.socketNodo.sendto(message, (ipDigitada, puerto))
							self.lockSocketNodo.release()

	#Metodo que envia el mensaje de suicidio a todos los vecinos
	def borrarme(self):
		mensajeAvisoMuerte = bytearray()
		mensajeAvisoMuerte += intToBytes(4,1)#Tipo de mensaje es 4
		mensajeAvisoMuerte += intToBytes(self.nodoId[1],1) #Se pone la mascara en el mensaje de solicitudes
		vecinos = self.tablaVecinos.obtenerVecinos()#Se piden todos los vecinos
		for x in vecinos:
			if self.tablaVecinos.obtenerBitActivo(x[0], x[1], x[2]) :
				self.lockSocketNodo.acquire()
				self.socketNodo.sendto( mensajeAvisoMuerte, (x[0], x[2]) )
				self.lockSocketNodo.release()
			else:
				print(str(x) + " vecino no activo ELIMINAR MENSAJE")

	#Metodo que despliega el menu de comunicacion con el usuario
	def despligueMenuUDP(self):
		bandera = True
		while bandera == True:
			print( "Soy el nodo " + str(self.nodoId) )
			print('Menu principal del modulo de Red UDP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Cambiar costo de enlace con un vecino. \n'
					'\t3. Imprimir tabla de alcanzabilidad.\n'
					'\t4. Imprimir tabla de vecinos.\n'
					'\t5. Cerrar nodo.')
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				print('Opcion deshabilitada')
				#self.envioMensajeUDP()
			elif taskUsuario == '2':
				print("\n\n")
				print('Opcion deshabilitada')
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