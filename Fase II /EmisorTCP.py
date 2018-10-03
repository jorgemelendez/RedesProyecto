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
from ConexionAbierta import *

class EmisorTCP:
	#Objeto para guardar conexiones
	conexiones = list()

	lockConexiones = threading.Lock()

	mensajesRecibidos = MensajesRecibidos()

	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.conexiones = list()
		self.lockConexiones = threading.Lock()

	#Llamar solo SIN candado adquirido
	def imprimirConexionesExistentes(self):
		self.lockConexiones.acquire()
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			print(self.conexiones[i].ip + " " + str(self.conexiones[i].puerto) )
			i = i + 1
		self.lockConexiones.release()

	#Llamar solo CON candado adquirido
	def hacerConexion(self, ip,puerto):
		#se crea el socket para enviar
		socketEmisorTCP = socket.socket()
		conexion = ConexionAbierta(ip,puerto,socketEmisorTCP)
		#Se establece la conexion con el receptorTCP mediante la ip y el puerto
		try:
			socketEmisorTCP.connect((ip, puerto))
		except SocketError:
			print("Fallo de conexion")
			return False
		else:
			print("Conexion establecida")
			self.conexiones.append(conexion)
			return True

	#Llamar solo CON candado adquirido
	def buscarConexion(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexion(ip,puerto) :
				return i
			i = i + 1
		return -1

	#Llamar solo CON candado adquirido
	def cerrarUnaConexion(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexion(ip,puerto) :
				self.conexiones[i].cerrarConexion()
				self.conexiones.remove(self.conexiones[i])
				break
			i = i + 1

	#Llamar solo CON candado adquirido
	def cerrarConexiones(self):
		while len(self.conexiones) != 0:
			self.conexiones[0].cerrarConexion()
			self.conexiones.remove(self.conexiones[0])

	#NO necesita tener candado
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

	#NO necesita tener candado
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

	#Llamar solo SIN candado adquirido
	def enviarMensaje(self):
		#self.lockConexiones.acquire()
		ip = input("Digite la ip del destinatario: ")
		ipPrueba = ip + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			puerto = input("Digite el puerto del destinatario: ")
			try:
				n = int(puerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if n < 0 or n > 65535:
					print ("Puerto no valido")
				else:
					self.lockConexiones.acquire()
					indice = self.buscarConexion(ip,int(puerto))

					if indice == -1:
						exito = self.hacerConexion(ip,int(puerto))
						if exito:
							print("Nueva conexion")
							mensaje = self.leerMensaje()
							respEnvio = self.conexiones[len(self.conexiones)-1].enviarMensaje(mensaje)
							if respEnvio == False:
								self.cerrarUnaConexion(ip,int(puerto))
							if len(mensaje) == 3:
								self.conexiones.pop(len(self.conexiones)-1)
					else:
						print("Conexion existente")
						mensaje = self.leerMensaje()
						respEnvio = self.conexiones[indice].enviarMensaje(mensaje)
						if respEnvio == False:
							self.cerrarUnaConexion(ip,int(puerto))
						if len(mensaje) == 3:
							self.conexiones.pop(indice)
					self.lockConexiones.release()

	#Llamar solo SIN candado adquirido
	def borrarme(self):
		#self.lockConexiones.acquire()
		mensaje = bytearray((1).to_bytes(2, byteorder='big'))# cant tuplas
		mensaje += (0).to_bytes(1, byteorder='big')

		i = 0
		self.lockConexiones.acquire()
		cant = len(self.conexiones)
		while i < cant:
			self.conexiones[i].enviarMensaje(mensaje)
			i = i + 1
		self.cerrarConexiones()
		self.lockConexiones.release()
		return

	#NO necesita tener candado
	def menu(self):
		
		bandera = True
		while bandera == True:
			print('Menu principal del modulo de Red TCP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Ver mensajes recibidos. \n'
					'\t3. Imprimir tabla de alcanzabilidad. \n'
					'\t4. Conexiones existentes. \n'
					'\t5. Cerrar nodo.')
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				self.enviarMensaje()
			elif taskUsuario == '2':
				print("\n\n")
				print('Mensajes recibidos:')
				self.mensajesRecibidos.imprimirMensajes()
				print("\n\n")
			elif taskUsuario == '3':
				print("\n\n")
				print('Tabla de alcanzabilidad:')
				self.tablaAlcanzabilidad.imprimirTabla()
				print("\n\n")
			elif taskUsuario == '5':
				bandera = False
				self.borrarme()
				print('Salida.')
				os._exit(1)
				#proceso_repetorTcp.exit()
			elif taskUsuario == '4':
				print("Conexiones existentes:")
				self.imprimirConexionesExistentes()
			else:
				print('Ingrese una opcion valida.')