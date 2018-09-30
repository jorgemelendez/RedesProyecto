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
from Mensaje import *

class ReceptorTCP:
	mensajesRecibidos = MensajesRecibidos()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def __init__(self,mensajesRecibidos, tablaAlcanzabilidad):
		self.mensajesRecibidos = mensajesRecibidos
		self.tablaAlcanzabilidad = tablaAlcanzabilidad

	def establecerConexion(self, conexion, addr):
		while True:
			#Recibimos el mensaje, con el metodo recv recibimos datos y como parametro 
			#la cantidad de bytes para recibir
			try:
				recibido = conexion.recv(2048)
			except SocketError:
				print("Conexion Perdida")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(addr[0],addr[1])
				break

			if(recibido == b''):#Salida para cuando el otro muere antes de mandar el primer mensaje
				print("Conexion Perdida")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(addr[0],addr[1])
				break

			cantTuplas = int(codecs.encode(recibido[0:2], 'hex_codec'))
			#mensajeSalir = int.from_bytes( recibido[2:3], byteorder='big' )
			#Si el mensaje recibido es la palabra close se cierra la aplicacion
			if cantTuplas == 1 and len(recibido) == 3:
				print("Conexion Terminada")
				self.tablaAlcanzabilidad.borrarFuenteDesdeAfuera(addr[0],addr[1])
				break
			
			mensaje = Mensaje(addr[0],addr[1],recibido)
			self.mensajesRecibidos.guardarMensaje(mensaje)
			self.mensajesRecibidos.imprimirMensaje(mensaje) 
			self.tablaAlcanzabilidad.actualizarTabla(mensaje)
			
		conexion.close()

	def recibir(self,ip,puerto):
		#instanciamos un objeto para trabajar con el socket
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		 
		s.bind((ip,puerto))
		 
		s.listen(5)
		
		while True:
			conexion, addr = s.accept()
			
			thread_servidor = threading.Thread(target=self.establecerConexion, args=(conexion,addr))
			thread_servidor.start()
			print("Conexion recibida")
		
		#Cerramos la instancia del socket cliente y servidor
		s.close()