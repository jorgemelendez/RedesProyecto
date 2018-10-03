import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError
from ArmarMensajes import *
from LeerArchivo import *

class ConexionLogicaUDP:
	otroIpRec = ""
	otroPuertoRec = 0

	miIpRec = ""
	miPuertoRec = 0
	
	miSocketEmisor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	hiloFuncionando = False

	datosRecibidos = bytearray()
	
	#otroIpRec		: Ip por donde me hablo para establecer conexion
	#otroPuertoRec	: Puerto por donde me hablo para establecer conexion
	#miIpRec		: Ip por donde me hablo para establecer conexion
	#miPuertoRec	: Puerto por donde me hablo para establecer conexion
	def __init__(self, otroIpRec, otroPuertoRec, miIpRec, miPuertoRec):
		self.otroIpRec = otroIpRec
		self.otroPuertoRec = otroPuertoRec
		self.miIpRec = miIpRec
		self.miPuertoRec = miPuertoRec
		self.hiloFuncionando = False
		self.datosRecibidos = bytearray()

	def activarHiloFuncionando(self):
		self.hiloFuncionando = False

	def annadirDatosRecibidos(self,datosNuevos):
		self.datosRecibidos += datosNuevos
		#Enviar paquete de ack de respuesta
		ACK = armarPaq(self.miIpRec,self.miPuertoRec,self.otroIpRec,self.otroPuertoRec,10,SNoRN, datos)
		socketACK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		socketACK.sendto(ACK, (self.otroIpRec, self.otroPuertoRec))
		socketACK.close()

	def soyLaConexionDesde(self,miIpRec,miPuertoRec):
		if self.miIpRec == miIpRec and self.miPuertoRec == miPuertoRec:
			return True
		return False

	def soyLaConexionHacia(self,otroIpRec,otroPuertoRec):
		if self.otroIpRec == otroIpRec and self.otroPuertoRec == otroPuertoRec:
			return True
		return False

	def connect(self, ipServidor, puertoServidor):
		self.miSocketEmisor = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.miSocketEmisor.settimeout(0.5)##AAAAAAAAAVERIGUAR CUANTO DEBERIA DE SER
		llegoSYN = False
		intento = 1
		mensaje = armarPaq(self.miIpRec,self.miPuertoRec,self.otroIpRec,self.otroPuertoRec,1,0, bytearray())
		while llegoSYN == False:
			self.miSocketEmisor.sendto(mensaje, (ipServidor, puertoServidor))
			try:
				SYN, address = self.miSocketEmisor.recvfrom(1024)
			except socket.timeout:
				intento = intento + 1
				if intento == 10:# ver si se aumenta mas
					intento = 0
					print("Esa Ip con ese Puerto no esta escuchando")
					break
			else:
				tipo = bytesToInt(SYN[12:13])
				
				if tipo == 5:
					print("Recibi mensaje")
					#No hago nada con el puerto receptor porque ya lo conozco
					llegoSYN = True
					mensaje = armarPaq(self.miIpRec,self.miPuertoRec,self.otroIpRec,self.otroPuertoRec,6,0, bytearray())
					self.miSocketEmisor.sendto(mensaje, (ipServidor, puertoServidor))

		if llegoSYN:
			print("Conexion establecida")
		else:
			print("Conexion Fallida")
			self.miSocketEmisor.close()
		return llegoSYN

	def send(self,datos):
		segmentado = segmentarArchivo(datos, 5)#Definido de 5 bytes					
		i = 0
		largo = len(segmentado)
		SN = 0
		while i < largo:
			tramaSN = armarPaq(self.miIpRec,self.miPuertoRec,self.otroIpRec,self.otroPuertoRec,16,SN, segmentado[i])
			self.miSocketEmisor.settimeout(0.5)##AAAAAAAAAVERIGUAR CUANTO DEBERIA DE SER
			llegoACK = False
			intento = 0
			while llegoACK == False:
				self.miSocketEmisor.sendto(tramaSN, (self.otroIpRec, self.otroPuertoRec))
				try:
					ACK, address = self.miSocketEmisor.recvfrom(1024)
				except socket.timeout:
					intento = intento + 1
					print("No llego ACK")
				else:
					intento = 0
					tipo = int.from_bytes( ACK[0:1], byteorder='big')
					RN = int.from_bytes( ACK[1:2], byteorder='big')
					if tipo == 20 and RN > SN:
						SN = RN
						llegoACK = True
						i = i + 1
						#print(ACK)
	
	def close(self):
		self.miSocketEmisor.close()