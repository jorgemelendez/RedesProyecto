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
from LeerArchivo import *
from ConexionLogicaUDP import *


#contenido  = archivoToString("/home/christofer/Escritorio/RedesProyecto/ArchivoPrueba.txt")
#segmentado = segmentarArchivo(contenido, 3)

"""i = 0
largo = len(segmentado)
while i < largo:
	print(segmentado[i])
	print (len(segmentado[i]))
	i = i + 1"""
class EmisorUDP:

	conexiones = list()
	lockConexiones = threading.Lock()

	miIpServidor = "172.16.105.251"
	miPuertoServidor = 10000

	def __init__(self):
		self.conexiones = list()
		self.lockConexiones = threading.Lock()

	#Llamar solo CON candado adquirido
	def buscarConexionLogica(self, ip,puerto):#APLICA SI LAS CONEXIONES DEBEN ESTAR PARA AMBOS , creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, VER QUE DICE LA PROFE
		i = 0;
		largo = len(self.conexiones)
		while i < largo:
			if self.conexiones[i].soyLaConexionHacia(ip,puerto) :
				return i
			i = i + 1
		return -1

	
			

	

	def enviarArchivo(self):
		ipServidor = input('Digite la ip del destinatario: ')
		ipPrueba = ipServidor + "/32"
		try:
			n = ipaddress.ip_network(ipPrueba)
		except ValueError as e:
			print ("Ip no valida")
		else:
			lecturaPuerto = input('Digite el puerto del destinatario: ')
			try:
				puertoServidor = int(lecturaPuerto)
			except ValueError as e:
				print ("Puerto no valido")
			else:
				if puertoServidor < 0 or puertoServidor > 65535:
					print ("Puerto no valido")
				else:
					direccion = input('Digite la direccion del archivo: ')
					contenido = archivoToString(direccion)
					self.lockConexiones.acquire()
					indice = self.buscarConexionLogica(ipServidor, puertoServidor)# APLICA SOLO SI LA CONEXIONES DEBEN ESTAR EN AMBOS, creo que deben estar aunque para tener una lista de las conexiones hechas para usarlas, 

					if indice == -1:
						conexion = ConexionLogicaUDP( ipServidor, puertoServidor, self.miIpServidor, self.miPuertoServidor )
						exito = conexion.connect(ipServidor,puertoServidor)
						if exito:
							self.conexiones.append(conexion)
							print("Nueva conexion")
							respEnvio = self.conexiones[len(self.conexiones)-1].send(contenido)
							if respEnvio == False:
								self.cerrarUnaConexion(ip,int(puerto))
					
					else:
						print("Conexion existente")
						contenido = self.leerMensaje()
						respEnvio = self.conexiones[indice].enviarMensaje(contenido)
						if respEnvio == False:
							self.cerrarUnaConexion(ip,int(puerto))
						
					self.lockConexiones.release()


		

	




if __name__ == '__main__':
	emisor = EmisorUDP()
	emisor.enviarArchivo()