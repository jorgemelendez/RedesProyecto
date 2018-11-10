import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress


from ArmarMensajes import *
from socket import error as SocketError
from Red import *
from Fuente import *

class TablaAlcanzabilidad:
	tabla = list()
	lockTablaAlcanzabilidad = threading.Lock()
	
	def __init__(self):
		self.tabla = list()
		self.lockTablaAlcanzabilidad = threading.Lock()

	#Llamar solo CON candado adquirido
	def existeRed(self, ipRed, mascaraRed):
		#self.lockTablaAlcanzabilidad.acquire()
		i = 0
		largo = len(self.tabla)
		while i < largo:
			if self.tabla[i].soyEsaRed(ipRed, mascaraRed) :
				#self.lockTablaAlcanzabilidad.release()
				return i
			i = i + 1
		#self.lockTablaAlcanzabilidad.release()
		return -1

	#Llamar solo SIN candado adquirido
	def imprimirTabla(self):
		self.lockTablaAlcanzabilidad.acquire()
		i = 0
		largo = len(self.tabla)
		while i < largo:
			ipFuente = self.tabla[i].ipFuente
			puertoFuente = self.tabla[i].puertoFuente
			ipA = int.from_bytes( self.tabla[i].ipRed[0:1], byteorder='big' )
			ipB = int.from_bytes( self.tabla[i].ipRed[1:2], byteorder='big' )
			ipC = int.from_bytes( self.tabla[i].ipRed[2:3], byteorder='big' )
			ipD = int.from_bytes( self.tabla[i].ipRed[3:4], byteorder='big' )

			mascaraRed = int.from_bytes( self.tabla[i].mascaraRed, byteorder='big' )
			costo = int.from_bytes( self.tabla[i].costo, byteorder='big' )
			print(str(ipFuente) + " " + str(puertoFuente) + " " + str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + " " + str(mascaraRed) + " " + str(costo) )

			i = i + 1

		self.lockTablaAlcanzabilidad.release()

	#NO necesita tener candado
	def validarIP(self, ip,mascara):
		ipA = int.from_bytes( ip[0:1], byteorder='big' )
		ipB = int.from_bytes( ip[1:2], byteorder='big' )
		ipC = int.from_bytes( ip[2:3], byteorder='big' )
		ipD = int.from_bytes( ip[3:4], byteorder='big' )
		mas = int.from_bytes( mascara[0:1], byteorder='big' )

		ipcompleta = str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + "/" + str(mas)
		try:
			n = ipaddress.ip_network(ipcompleta) 
			return True
		except ValueError as e:
			return False

	#Llamar solo SIN candado adquirido
	def borrarFuenteDesdeAfuera(self,ipFuente, puetoFuente):
		self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a borrar fuente")
		i = 0
		largo = len(self.tabla)
		while i < largo:
			#print("while")
			if self.tabla[i].soyEsaFuente(ipFuente, puetoFuente) :
				self.tabla.pop(i)
				largo = largo - 1
			else:
				i = i + 1
		#print("Termine while")
		self.lockTablaAlcanzabilidad.release()

	#Llamar solo CON candado adquirido
	def borrarFuente(self,ipFuente, puetoFuente):
		#self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a borrar fuente")
		i = 0
		largo = len(self.tabla)
		while i < largo:
			#print("while")
			if self.tabla[i].soyEsaFuente(ipFuente, puetoFuente) :
				self.tabla.pop(i)
				largo = largo - 1
			else:
				i = i + 1
		#print("Termine while")
		#self.lockTablaAlcanzabilidad.release()

	#Llamar solo SIN candado adquirido
	def eliminarPrimerFuente(self):
		self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a eliminar primer fuente")
		i = 0
		largo = len(self.tabla)
		if largo > 0:
			ipFuente = self.tabla[i].ipFuente
			puertoFuente = self.tabla[i].puertoFuente
			#print("Mande a borrar fuente")
			self.borrarFuente(ipFuente,puertoFuente)
			#print("Volvi de borrar fuente")
			self.lockTablaAlcanzabilidad.release()
			return Fuente( ipFuente, puertoFuente )
		else:
			self.lockTablaAlcanzabilidad.release()
			return Fuente( "", 0 )

	#Llamar solo SIN candado adquirido
	def actualizarTabla(self, mensaje):
		#self.lockTablaAlcanzabilidad.acquire()

		ipFuenteNuevo = mensaje.ip
		puertoFuenteNuevo = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		while i < cantTuplas:
			ipRedNuevo = bytesMensaje[(i*8)+2:(i*8)+6]
			mascaraRedNuevo = bytesMensaje[(i*8)+6:(i*8)+7]
			costoNuevo = bytesMensaje[(i*8)+7:(i*8)+10]

			if self.validarIP(ipRedNuevo,mascaraRedNuevo):

				self.lockTablaAlcanzabilidad.acquire()
				exite = self.existeRed(ipRedNuevo, mascaraRedNuevo)
				if exite == -1 :
					#Se crea una nueva tupla
					self.tabla.append(Red(ipFuenteNuevo,puertoFuenteNuevo,ipRedNuevo, mascaraRedNuevo, costoNuevo))
				else:
					#se actualiza la tupla de ser necesario
					if self.tabla[exite].costoMenor(costoNuevo) :
						self.tabla[exite].actualizarRed(ipFuenteNuevo,puertoFuenteNuevo,ipRedNuevo, mascaraRedNuevo, costoNuevo);
					#Si el costo es mayor queda como antes
				self.lockTablaAlcanzabilidad.release()
			i = i + 1