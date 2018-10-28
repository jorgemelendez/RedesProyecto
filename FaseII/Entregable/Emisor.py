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
from Servidor import *
from BanderaFin import *
from HiloConexionUDPSegura import *

class Emisor:

	def __init__(self, miConexion, buzonReceptor, socketConexion, lockSocket, conexiones, lockConexiones, bitacora):
		self.conexiones = conexiones
		self.lockConexiones = lockConexiones
		self.miConexion = miConexion
		self.buzonReceptor = buzonReceptor
		self.socketConexion = socketConexion
		self.lockSocket = lockSocket
		self.bitacora = bitacora

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

	def enviarArchivo(self):
		otraIp = input('Digite la ip del destinatario: ')
		ipPrueba = otraIp + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			lecturaPuerto = input('Digite el puerto del destinatario: ')
			try:
				otroPuerto = int(lecturaPuerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if otroPuerto < 0 or otroPuerto > 65535:
					print ("Puerto no valido")
				else:
					direccion = input('Digite la direccion del archivo: ')
					contenido = archivoToString(direccion)
					self.lockConexiones.acquire()
					indice = self.buscarConexionLogica(otraIp, otroPuerto)
					if indice == -1:
						print ("Nueva conexion")
						conexion = HiloConexionUDPSegura( self.buzonReceptor, (otraIp,otroPuerto), self.miConexion, self.socketConexion, self.lockSocket, self.bitacora )
						conexion.connect(otraIp,otroPuerto)
						hiloNuevaConexion = threading.Thread(target=self.crearHiloConexion, args=(conexion,))
						hiloNuevaConexion.start()
						self.conexiones.append(conexion)
						self.bitacora.escribir("Emisor: cree la conexion" + otraIp + " " + str(otroPuerto) )
						self.lockConexiones.release()
						conexion.meterArchivoAEnviar(contenido)
						#print("Sali de enviar archivo 1")
					else:
						print("Conexion existente")
						self.lockConexiones.release()
						self.conexiones[indice].meterArchivoAEnviar(contenido)
						#print("Sali de enviar archivo 2")
					self.bitacora.escribir("Emisor: envie un archivo a " + otraIp + " " + str(otroPuerto) )
