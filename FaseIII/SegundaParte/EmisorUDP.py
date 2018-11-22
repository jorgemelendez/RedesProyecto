import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from TablaAlcanzabilidad import *
from ArmarMensajes import *

class EmisorUDP:

	#Constructor
	#nodoId: tupla id del nodo, (ip, mascara, puerto)
	#tablaAlcanzabilidad: tabla de alcanzabilidad del nodo
	#tablaVecinos: tabla de vecinos del nodo
	#socketNodo: socket del nodo
	#lockSocketNodo: lock del socket del nodo
	def __init__(self, nodoId, tablaAlcanzabilidad, tablaVecinos, socketNodo, lockSocketNodo, bitacora):
		self.bitacora = bitacora
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
					lecturaPuerto = input('Digite el puerto del destinatario: ')
					try:
						puerto = int(lecturaPuerto)
					except ValueError as e:
						print ("Puerto no valido")
					else:
						if puerto < 0 or puerto > 65535:
							print ("Puerto no valido")
						else:#Codigo para hacer y enviar el mensaje
							mensaje = input('Digite el mensaje que desea enviar: ')
							tamanno = len(mensaje)
							message = intToBytes(5,1)#Tipo de mensaje es 5
							message += ipToBytes(self.nodoId[0]) #Se pone la ip emisor en el mensaje
							#message += intToBytes(self.nodoId[1],1) #Se pone la mascara emisor en el mensaje
							message += intToBytes(self.nodoId[2],2) #Se pone el puerto emisor en el mensaje
							message += ipToBytes(ipDigitada) #Se pone la ip destino en el mensaje
							#message += intToBytes(mascara,1) #Se pone la mascara destino en el mensaje
							message += intToBytes(puerto,2) #Se pone el puerto destino en el mensaje
							message += intToBytes(tamanno,2)
							message += str.encode(mensaje)
							#AQUI VA EL PARSER
							sigNodo = self.tablaAlcanzabilidad.obtenerSiguienteNodo((ipDigitada,mascara,puerto))
							if sigNodo != None:
								self.lockSocketNodo.acquire()
								self.socketNodo.sendto(message, (sigNodo[0], sigNodo[2]))
								self.lockSocketNodo.release()
								self.bitacora.escribir("EmisorUDP: " + "Se envia el mensaje \"" + mensaje + "\" a (" + ipDigitada + "," + str(mascara) + "," + str(puerto) + ")" )
								self.bitacora.escribir("EmisorUDP: " + "El mensaje se envio atravez de " + str(sigNodo) )
							else:
								print("Ese nodo no se encuentra como uno de los alcanzables en la tabla de enrrutamiento")
								self.bitacora.escribir("EmisorUDP: " + "Ese nodo no se encuentra como uno de los alcanzables en la tabla de enrrutamiento")

	#Metodo que envia el mensaje de suicidio a todos los vecinos
	def borrarme(self):
		self.bitacora.escribir("EmisorUDP: " + "Usuario solicito cerrar el nodo")
		mensajeAvisoMuerte = bytearray()
		mensajeAvisoMuerte += intToBytes(7,1)#Tipo de mensaje es 7
		#mensajeAvisoMuerte += intToBytes(self.nodoId[1],1) #Se pone la mascara en el mensaje de solicitudes
		vecinos = self.tablaVecinos.obtenerVecinos()#Se piden todos los vecinos
		for x in vecinos:
			if self.tablaVecinos.obtenerBitActivo(x[0], x[1], x[2]) :
				self.lockSocketNodo.acquire()
				self.socketNodo.sendto( mensajeAvisoMuerte, (x[0], x[2]) )
				self.lockSocketNodo.release()
				self.bitacora.escribir("EmisorUDP: " + "Envie mensaje de muerte a " + str(x))

	def realizarCambio(self, key, distanciaNueva):
		existe = self.tablaVecinos.existeVecinoActivo(key)
		if existe:
			distanciaVieja = self.tablaVecinos.obtenerDistancia(key[0],key[1],key[2])
			self.tablaVecinos.modificarDistancia(key[0],key[1],key[2],distanciaNueva)
			message = intToBytes(6,1)#Tipo de mensaje es 6
			message += intToBytes(distanciaNueva,3)#Distancia nueva
			self.lockSocketNodo.acquire()
			self.socketNodo.sendto(message, (key[0], key[2]))
			self.lockSocketNodo.release()
		else:
			print("El nodo " + str(key) + " no es mi vecino o no esta vivo, por lo tanto no se puede cambiar el costo")

	def cambiarCosto(self):
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
					lecturaPuerto = input('Digite el puerto del destinatario: ')
					try:
						puerto = int(lecturaPuerto)
					except ValueError as e:
						print ("Puerto no valido")
					else:
						if puerto < 0 or puerto > 65535:
							print ("Puerto no valido")
						else:
							lecturaDistancia = input('Digite la nueva distancia: ')
							try:
								distancia = int(lecturaDistancia)
							except ValueError as e:
								print ("Distancia no valida")
							else:
								if distancia < 20 or distancia > 100:
									print ("Distancia no valida")
								else:
									self.realizarCambio((ipDigitada,mascara,puerto),distancia)


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
				#print('Opcion deshabilitada')
				self.envioMensajeUDP()
			elif taskUsuario == '2':
				print("\n\n")
				print('Cambiar costo con vecino')
				self.cambiarCosto()
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
				self.bitacora.escribir("Me voy a morir")
				self.bitacora.terminar()
				os._exit(1)
			else:
				print('Ingrese opcion valida.')