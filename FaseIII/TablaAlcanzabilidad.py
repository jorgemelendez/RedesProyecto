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

	#Constructor
	def __init__(self):
		#self.tabla = list()
		self.tabla = dict() #El formato va a ser:  key=(ip,mascara,puerto) valor=(costo,(ip,mascara,puerto))
		self.lockTablaAlcanzabilidad = threading.Lock()

	#Metodo que imprime la tabla de alcanzabilidad del nodo
	def imprimirTabla(self):
		llaves = self.tabla.keys()
		for x in llaves:
			valor = self.tabla[x]
			print( str(x) + " " + str(valor[0]) + " " + str(valor[1]) )

	#Metodo para validar que la ip que llego el valida
	#ip: ip a validad
	#mascara: mascara con la que se va a validar la ip
	def validarIP(self, ip, mascara):
		ipcompleta = ip + "/" + str(mascara)
		try:
			n = ipaddress.ip_network(ipcompleta) 
			return True
		except ValueError as e:
			return False

	#Metodo para borrar un alcanzable de la tabla
	#ip: ip del alcanzable que se quiere borrar
	#mascara: mascara del alcanzable que se quiere borrar
	#puerto: puerto del alcanzable que se quiere borrar
	def borrarAlcanzable(self,ip, mascara, puerto):
		self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a borrar fuente")
		del self.tabla[(ip, mascara, puerto)]
		#print("Termine while")
		self.lockTablaAlcanzabilidad.release()

	#Metodo para borrar un alcanzable de la tabla
	#ip: ip del alcanzable que se quiere borrar
	#mascara: mascara del alcanzable que se quiere borrar
	#puerto: puerto del alcanzable que se quiere borrar
	def borrarAtravez(self,ip, mascara, puerto):
		self.lockTablaAlcanzabilidad.acquire()
		#print("Entre a borrar fuente")
		listaEliminar = list()
		llaves = self.tabla.keys()
		for x in llaves:
			valor = self.tabla[x]
			if valor[1] == (ip,mascara,puerto):
				listaEliminar.append(x)
		for x in listaEliminar:
			del self.tabla[x]
		#print("Termine while")
		self.lockTablaAlcanzabilidad.release()

	#Llamar solo SIN candado adquirido
	#mensaje: actualizacion recibido (2bytes de cantidad de tuplas, 
	#      tuplas (ip,mascara,puerto,distancia))
	#atravezDe: tupla que es el intermediario entre el nodo y el destino, tupla (ip,mascara,puerto)
	def actualizarTabla(self, mensaje, atravezDe):
		#self.lockTablaAlcanzabilidad.acquire()

		bytesMensaje = mensaje

		cantTuplas = bytesToInt( bytesMensaje[0:2] )
		i = 0
		while i < cantTuplas:
			ipNuevo = bytesToIp( bytesMensaje[(i*8)+2:(i*8)+6] )
			mascaraNuevo = bytesToInt( bytesMensaje[(i*8)+6:(i*8)+7] )
			puertoNuevo = bytesToInt( bytesMensaje[(i*8)+7:(i*8)+9] )
			distanciaNuevo = bytesToInt( bytesMensaje[(i*8)+9:(i*8)+10] )

			x = ipNuevo, mascaraNuevo, puertoNuevo #Se hace la tupla de key

			#if self.validarIP(ipNuevo,mascaraNuevo): #Se valida la IP del mensaje

			self.lockTablaAlcanzabilidad.acquire()
			exite = self.tabla.get(x)
			if exite == None : #Si una entrada con ese Key NO existe, se crea
				#Se crea una nueva tupla
				self.tabla[x] = distanciaNuevo, atravezDe
			else:#Si existe una entrada con ese Key, se actualiza el valor de ser necesario
				#Se pregunta si el costo recibido es menor al que tenia, en caso de que si se atualiza
				if exite[0] > distanciaNuevo:
					self.tabla[x] = distanciaNuevo, atravezDe
					#FALTA MANDAR A BITACORA
			self.lockTablaAlcanzabilidad.release()
			#else:
			#	print("Se ignora " + str(x) + " porque no es una IP valida en esa mascara")
			i = i + 1




#if __name__ == '__main__':
#	tablaAlcanzabilidad = TablaAlcanzabilidad()
#	mensaje = bytearray()
#	mensaje += intToBytes(4,2)
#	mensaje +=  ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(9000,2) + intToBytes(70,1)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(10000,2) + intToBytes(80,1)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(11000,2) + intToBytes(51,1)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(12000,2) + intToBytes(42,1)
#	
#	tablaAlcanzabilidad.actualizarTabla(mensaje,("192.168.100.17", 24, 4000))
#
#	mensaje = intToBytes(1,2)
#	mensaje +=	ipToBytes("192.168.100.17") + intToBytes(24,1) + intToBytes(13000,2) + intToBytes(42,1)
#	
#	tablaAlcanzabilidad.actualizarTabla(mensaje,("192.168.100.17", 24, 5000))
#
#	tablaAlcanzabilidad.imprimirTabla()
#
#	print("\n\n\n")
#	tablaAlcanzabilidad.borrarAlcanzable("192.168.100.17", 24, 9000)
#	tablaAlcanzabilidad.imprimirTabla()
#
#	print("\n\n\n")
#	tablaAlcanzabilidad.borrarAlcanzable("192.168.100.17", 24, 11000)
#	tablaAlcanzabilidad.imprimirTabla()
#
#	print("\n\n\n")
#	tablaAlcanzabilidad.borrarAtravez("192.168.100.17", 24, 4000)
#	tablaAlcanzabilidad.imprimirTabla()