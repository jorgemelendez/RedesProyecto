import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError

class ConexionAbierta:

	def __init__(self,ip,puerto,socketEmisorTCP):
		self.socketEmisorTCP = socketEmisorTCP
		self.ip = ip
		self.puerto = puerto

	def enviarMensaje(self,mensaje):
		try:
			sent = self.socketEmisorTCP.send(mensaje)
		except SocketError as e:
				print("ERROR AL ENVIAR EL MENSAJE, Conexion no disponible")
				return False
		else:
			if sent == 0:
				print("ERROR AL ENVIAR EL MENSAJE, Conexion no disponible")
				return False
		return True

	def cerrarConexion(self):
		self.socketEmisorTCP.close()

	def soyLaConexion(self,ip,puerto):
		if self.ip == ip and self.puerto == puerto:
			return True
		
		return False