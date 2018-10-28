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
from Servidor import *
from BanderaFin import *
from HiloConexionUDPSegura import *

class pseudoTCPSobreUDP:

	def __init__(self, miConexion):
		self.miConexion = miConexion
		self.bitacora = Bitacora("Bitacora-("+miConexion[0]+","+str(miConexion[1])+").txt")
		self.socketConexion = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.socketConexion.bind(self.miConexion)
		self.lockSocket = threading.Lock()
		self.buzonReceptor = Buzon()
		self.conexiones = list()
		self.lockConexiones = threading.Lock()
		self.emisor = Emisor( self.miConexion, self.buzonReceptor, self.socketConexion, self.lockSocket, self.conexiones, self.lockConexiones, self.bitacora)
		self.lockFin = threading.Lock()
		self.banderaFin = BanderaFin(False)
		self.servidor = Servidor( self.miConexion, self.buzonReceptor, self.socketConexion, self.lockSocket, self.conexiones, self.lockConexiones, self.bitacora, self.banderaFin)

	def cerrarUnaConexion(self):
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
					i = 0;
					encontre = False
					self.lockConexiones.acquire()
					largo = len(self.conexiones)
					while i < largo:
						if self.conexiones[i].soyLaConexionHacia(otraIp,otroPuerto):
							self.conexiones[i].close()
							encontre = True
							break
						i = i + 1
					self.lockConexiones.release()
					if encontre == False:
						print("La conexion (" + otraIp + "," + str(otroPuerto) + ") no existia")
						self.bitacora.escribir("La conexion (" + otraIp + "," + str(otroPuerto) + ") no existia")
					else:
						print("La conexion (" + otraIp + "," + str(otroPuerto) + ") se envio a cerrar")
						self.bitacora.escribir("La conexion (" + otraIp + "," + str(otroPuerto) + ") se envio a cerrar")

	def cerrarTodo(self):
		self.lockConexiones.acquire()
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			self.conexiones[i].close()
			i = i + 1
		self.lockConexiones.release()
		print("Se envio a cerrar cada una de las conexiones")
		self.bitacora.escribir("Se envio a cerrar cada una de las conexiones")

	def menu(self):
		bandera = True
		while bandera == True:
			print('Menu principal del modulo de Red TCP: \n'
					'\t1. Enviar un archivo. \n'
					'\t2. Cerrar conexiones. \n'
					'\t3. Cerrar una conexion especifica. \n'
					'\t4. Salir. \n')
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				self.emisor.enviarArchivo()
			elif taskUsuario == '2':
				self.cerrarTodo()
			elif taskUsuario == '3':
				self.cerrarUnaConexion()
			elif taskUsuario == '4':
				self.banderaFin.modificarBandera(True)
				break
			else:
				print('Ingrese una opcion valida.')

	def iniciar(self):
		threadEmisor = threading.Thread(target=self.servidor.cicloServidor, args=())
		threadEmisor.start()
		self.menu()
		self.bitacora.terminar()
		#print("Emisor termine")

if __name__ == '__main__':
	prueba = pseudoTCPSobreUDP((sys.argv[1],int(sys.argv[2])))
	prueba.iniciar()