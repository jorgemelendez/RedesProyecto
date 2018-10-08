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

	RN = 0
	
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
		self.RN = 0

	def activarHiloFuncionando(self):
		self.hiloFuncionando = False

	def recv(self, emisor,recibido):
		otroIpRec = bytesToIp(recibido[0:4])
		#print(otroIpRec)
		otroPuertoRec = bytesToInt(recibido[4:6])
		#print(otroPuertoRec)
		miIpRec = bytesToIp(recibido[6:10])
		#print(miIpRec)
		miPuertoRec = bytesToInt(recibido[10:12])
		#print(miPuertoRec)
		tipoPaq = bytesToInt(recibido[12:13])
		secuencia = bytesToInt(recibido[13:14])
		datos = recibido[13:]

		print("SN")
		print(secuencia)
		print("RN")
		print(self.RN)
		if secuencia == self.RN:
			print("ENTRE")
			self.datosRecibidos += datos
			#Enviar paquete de ack de respuesta
			self.RN = self.RN + 1

			ACK = armarPaq(miIpRec,miPuertoRec,otroIpRec,otroPuertoRec,20,self.RN, bytearray())
			socketACK = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			print(otroIpRec)
			print(otroPuertoRec)
			socketACK.sendto(ACK, emisor)
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
				print("aqui")
				print(self.miPuertoRec)
				print("aqui")
				self.miSocketEmisor.sendto(tramaSN, (self.otroIpRec, self.otroPuertoRec))
				try:
					ACK, address = self.miSocketEmisor.recvfrom(1024)
				except socket.timeout:
					intento = intento + 1
					print("No llego ACK")
				else:
					print("AAAAQIO")
					intento = 0
					tipo = int.from_bytes( ACK[12:13], byteorder='big')
					RNrecibido = int.from_bytes( ACK[13:14], byteorder='big')
					print(tipo)
					print(RNrecibido)
					if tipo == 20 and RNrecibido > SN:
						SN = RNrecibido
						llegoACK = True
						i = i + 1
						#print(ACK)
	
	def close(self):
		self.miSocketEmisor.close()