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
from ArmarMensajes import *
from ConexionLogicaUDP import *

class ReceptorUDP:
	mensajesRecibidos = MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	conexiones = list()
	lockConexiones = threading.Lock()

	posiblesConexiones = list()
	lockPosiblesConexiones = threading.Lock()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad
		self.conexiones = list()#DEBE ENTRAR POR PARAMETRO EN CASO DE QUE LAS CONEXIONES LAS TENGAN EMISOR Y RECEPTOR
		self.lockConexiones = threading.Lock()#DEBE ENTRAR POR PARAMETRO EN CASO DE QUE LAS CONEXIONES LAS TENGAN EMISOR Y RECEPTOR
		self.posiblesConexiones = list()
		self.lockPosiblesConexiones = threading.Lock()

	#Llamar solo SIN candado adquirido
	def imprimirConexionesLogicas(self):
		self.lockConexiones.acquire()
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			print(self.conexiones[i].ip + " " + str(self.conexiones[i].puerto) )
			i = i + 1
		self.lockConexiones.release()

	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	#Llamar solo CON candado adquirido
	def buscarPosibleConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.posiblesConexiones)
		while i < largo:
			if self.posiblesConexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def accept(self, serverSocket, emisor, recibido):
		#Establecer RN = 0, poner en la estructura de la conexion un buffer y este RN
		
		otroIpRec = bytesToIp(recibido[0:4])
		print(otroIpRec)
		otroPuertoRec = bytesToInt(recibido[4:6])
		print(otroPuertoRec)
		miIpRec = bytesToIp(recibido[6:10])
		print(miIpRec)
		miPuertoRec = bytesToInt(recibido[10:12])
		print(miPuertoRec)
		tipoPaq = bytesToInt(recibido[12:13])
		secuencia = bytesToInt(recibido[13:14])#OJO SI SE CAMBIA A MAS GRANDE AL SECUENCIA


		#ver si  hay que verificar que la conexion no exista
		conexionNueva = ConexionLogicaUDP(otroIpRec, otroPuertoRec, miIpRec, miPuertoRec)
		
		mensaje = armarPaq(miIpRec,miPuertoRec,otroIpRec,otroPuertoRec,5,0, bytearray())
		
		serverSocket.sendto(mensaje, (emisor[0], emisor[1]))
		#SE METE A UNA LISTA DE POSIBLES COENXIONES

		self.lockPosiblesConexiones.acquire()

		self.posiblesConexiones.append(conexionNueva)

		self.lockPosiblesConexiones.release()

	def finalaccept(self,recibido):
		otroIpRec = bytesToIp(recibido[0:4])
		otroPuertoRec = bytesToInt(recibido[4:6])
		miIpRec = bytesToIp(recibido[6:10])
		miPuertoRec = bytesToInt(recibido[10:12])
		tipoPaq = bytesToInt(recibido[12:13])
		secuencia = bytesToInt(recibido[13:14])#OJO SI SE CAMBIA A MAS GRANDE AL SECUENCIA

		self.lockPosiblesConexiones.acquire()

		indice = self.buscarPosibleConexionLogica(otroIpRec,otroPuertoRec)

		if indice == -1:
			print("Llego un finSyn sin que exista un syn")
		else:
			conexionestablecida = self.posiblesConexiones.pop(indice)
			self.lockConexiones.acquire()
			self.conexiones.append(conexionestablecida)
			self.lockConexiones.release()
			print("Conexion Establecida")

		self.lockPosiblesConexiones.release()
		



	#Algoritmo ARQRECEPTOR
	def paqueteConDatos(self, emisor, recibido):
		otroIpRec = bytesToIp(recibido[0:4])
		print(otroIpRec)
		otroPuertoRec = bytesToInt(recibido[4:6])
		print(otroPuertoRec)
		miIpRec = bytesToIp(recibido[6:10])
		print(miIpRec)
		miPuertoRec = bytesToInt(recibido[10:12])
		print(miPuertoRec)
		tipoPaq = bytesToInt(recibido[12:13])
		secuencia = bytesToInt(recibido[13:14])
		datos = recibido[13:]


		self.lockConexiones.acquire()
		indice = self.buscarConexionLogica(otroIpRec, otroPuertoRec)

		if indice == -1:
			print("Paquete de conexion no establecida")
		else:
			self.conexiones[indice].annadirDatosRecibidos(datos)
		self.lockConexiones.release()
		
		


	def listen(self, ip, puerto):
		#self.lockMensajesRecibidos.acquire()
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		serverSocket.bind((ip, puerto))
		
		while 1:#CREAR UN HILO PARA QUE PROCESE CADA MENSAJE RECIBIDO
			mensaje, add = serverSocket.recvfrom(2048)
			if bytesToInt(mensaje[12:13]) == 1:# Mensaje para establecer conexion
				self.accept(serverSocket, add, mensaje)
			elif bytesToInt(mensaje[12:13]) == 6:# Mensaje ack de establecer conexion(fin de establecimiento de conexion)
				self.finalaccept(mensaje)
			elif bytesToInt(mensaje[12:13]) == 16:# Mensaje de datos
				if randrange(10) > 1:
					self.paqueteConDatos(add, mensaje)


if __name__ == '__main__':
	mensajesRecibidos= MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()
	servidorUDP = ReceptorUDP(mensajesRecibidos, tablaAlcanzabilidad)
	proceso_receptorUDP = threading.Thread(target=servidorUDP.listen, args=("192.168.0.15",5000,))
	proceso_receptorUDP.start()