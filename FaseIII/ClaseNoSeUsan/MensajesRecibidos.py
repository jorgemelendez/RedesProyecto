import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress

from socket import error as SocketError

class MensajesRecibidos:
	mensajesRecibidos = list()
	lockMensajesRecibidos = threading.Lock()

	def __init__(self):
		self.mensajesRecibidos = list()
		self.lockMensajesRecibidos = threading.Lock()

	#Llamar solo SIN candado adquirido
	def guardarMensaje(self,mensaje):
		self.lockMensajesRecibidos.acquire()
		self.mensajesRecibidos.append(mensaje)
		self.lockMensajesRecibidos.release()

	#NO necesita tener candado
	def imprimirMensaje(self, mensaje):
		ip = mensaje.ip
		puerto = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		#print("\n\nIPf = " + str(ip) + " Puerto = " + str(puerto) + " Envio el siguiente mensaje: ")
		print("IPf = " + str(ip) + " Puerto = " + str(puerto) + " Envio el siguiente mensaje: ")
		while i < cantTuplas:
			ipA = int.from_bytes( bytesMensaje[(i*8)+2:(i*8)+3], byteorder='big' )
			ipB = int.from_bytes( bytesMensaje[(i*8)+3:(i*8)+4], byteorder='big' )
			ipC = int.from_bytes( bytesMensaje[(i*8)+4:(i*8)+5], byteorder='big' )
			ipD = int.from_bytes( bytesMensaje[(i*8)+5:(i*8)+6], byteorder='big' )
			mascara = int.from_bytes( bytesMensaje[(i*8)+6:(i*8)+7], byteorder='big' )
			costo = int.from_bytes( bytesMensaje[(i*8)+7:(i*8)+10], byteorder='big' )
			print( str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + " " + str(mascara) + " " + str(costo) )
			i = i + 1
		#print("\n\n")

	#Llamar solo SIN candado adquirido
	def imprimirMensajes(self):
		self.lockMensajesRecibidos.acquire()
		i = 0
		largo = len(self.mensajesRecibidos)
		while i < largo:
			self.imprimirMensaje( self.mensajesRecibidos[i] )
			i = i + 1
		self.lockMensajesRecibidos.release()