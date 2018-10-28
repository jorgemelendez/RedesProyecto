import sys
import time
import socket
import threading
import datetime
import os
from random import randrange

from ArmarMensajes import *
from LeerArchivo import *
from Buzon import *
from Bitacora import *
from Emisor import *
from BanderaFin import *
from HiloConexionUDPSegura import *

class Servidor:
	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones, bitacora, banderaFin):
		self.conexiones = conexiones
		self.lockConexiones = lockConexiones
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.bitacora = bitacora
		self.banderaFin = banderaFin

	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	def crearHiloConexion(self, conexion):
		conexion.receptor()
		#print("Antes del terminar")
		self.lockConexiones.acquire()
		#print("Despues del lock")
		self.conexiones.remove(conexion)
		self.lockConexiones.release()
		#print("Libere el lock 1")

	def cicloServidor(self):
		self.bitacora.escribir("Servidor: Inicie")
		while True:
			#self.lockSocket.acquire()
			self.socketConexion.settimeout(1)
			try:
				recibido, clientAddress = self.socketConexion.recvfrom(2048)
			except socket.timeout:
				x=0
				#self.lockSocket.release()
			else:
				#self.socketConexion.settimeout(0)
				#self.lockSocket.release()
				self.lockConexiones.acquire()
				existeConexion = self.buscarConexionLogica( clientAddress[0], clientAddress[1])
				if existeConexion != -1 :
					tipoPaq = bytesToInt(recibido[12:13])
					random = randrange(10)
					if random>1:
						self.buzonReceptor.meterDatos(clientAddress, recibido)
					else:
						self.bitacora.escribir("Servidor: se elimino un paquete que recibi")
				else:
					tipoPaq = bytesToInt(recibido[12:13])
					if tipoPaq == 1:
						self.buzonReceptor.meterDatos(clientAddress, recibido)
						self.bitacora.escribir("Servidor: cree la conexion " + clientAddress[0] + " " + str(clientAddress[1]) )
						conexion = HiloConexionUDPSegura( self.buzonReceptor, clientAddress, self.miConexion, self.socketConexion, self.lockSocket, self.bitacora)
						self.conexiones.append(conexion)
						hiloNuevaConexion = threading.Thread(target=self.crearHiloConexion, args=(conexion,))
						hiloNuevaConexion.start()
					else:
						self.bitacora.escribir("("+clientAddress[0] + "," +str(clientAddress[1])+")")
						self.bitacora.escribir("ESTA CONEXION NO EXITE Y LLEGO UN MENSAJE DISTINTO A SYN")
				self.lockConexiones.release()
			if self.banderaFin.leerBandera():
				break
