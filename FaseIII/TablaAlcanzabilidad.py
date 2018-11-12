import sys
import threading
import socket
import errno
import codecs
import os
import ipaddress


from ArmarMensajes import *
from socket import error as SocketError

class TablaAlcanzabilidad:

	#Constructor
	def __init__(self, bitacora):
		self.bitacora = bitacora
		self.tabla = dict() #El formato va a ser:  key=(ip,mascara,puerto) valor=(costo,(ip,mascara,puerto))
		self.lockTablaAlcanzabilidad = threading.Lock()

	#Metodo que imprime la tabla de alcanzabilidad del nodo
	def imprimirTabla(self):
		self.lockTablaAlcanzabilidad.acquire()
		llaves = self.tabla.keys()
		for x in llaves:
			valor = self.tabla[x]
			print( str(x) + " " + str(valor[0]) + " " + str(valor[1]) )
		self.lockTablaAlcanzabilidad.release()

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
	# borra la tupla con llave (ip,mascara,puerto)
	#ip: ip del alcanzable que se quiere borrar
	#mascara: mascara del alcanzable que se quiere borrar
	#puerto: puerto del alcanzable que se quiere borrar
	def borrarAlcanzable(self,ip, mascara, puerto):
		self.lockTablaAlcanzabilidad.acquire()
		del self.tabla[(ip, mascara, puerto)]
		self.lockTablaAlcanzabilidad.release()
		self.bitacora.escribir("TablaAlcanzabilidad: " + "Se borra el alcanzable " + str((ip,mascara,puerto)))

	#Metodo para borrar un alcanzable de la tabla
	# borra las tuplas que su a traves ser (ip,mascara,puerto)
	#ip: ip del alcanzable que se quiere borrar
	#mascara: mascara del alcanzable que se quiere borrar
	#puerto: puerto del alcanzable que se quiere borrar
	def borrarAtravez(self,ip, mascara, puerto):
		self.lockTablaAlcanzabilidad.acquire()
		listaEliminar = list()
		llaves = self.tabla.keys()
		for x in llaves:
			valor = self.tabla[x]
			if valor[1] == (ip,mascara,puerto):
				listaEliminar.append(x)
		for x in listaEliminar:
			del self.tabla[x]
		self.lockTablaAlcanzabilidad.release()
		self.bitacora.escribir("TablaAlcanzabilidad: " + "Se borra todos los alcanzables que se llegaba a traves de" + str((ip,mascara,puerto)))

	#Metodo para actualizar la tabla cuando llega un mensaje de actializacio de tabla
	#mensaje: actualizacion recibido (2bytes de cantidad de tuplas, 
	#      tuplas (ip,mascara,puerto,distancia))
	#atravezDe: tupla que es el intermediario entre el nodo y el destino, tupla (ip,mascara,puerto)
	#distanciaAtravezDe: distancia del vecino para tomarla en cuenta en la actualizacion
	def actualizarTabla(self, mensaje, atravezDe, distanciaAtravezDe):
		self.lockTablaAlcanzabilidad.acquire()#Se agarra el candadi aqui para que la actualizacion se de completa
		bytesMensaje = mensaje
		cantTuplas = bytesToInt( bytesMensaje[0:2] )
		i = 0
		while i < cantTuplas:
			ipNuevo = bytesToIp( bytesMensaje[(i*10)+2:(i*10)+6] )
			mascaraNuevo = bytesToInt( bytesMensaje[(i*10)+6:(i*10)+7] )
			puertoNuevo = bytesToInt( bytesMensaje[(i*10)+7:(i*10)+9] )
			distanciaNuevo = bytesToInt( bytesMensaje[(i*10)+9:(i*10)+12] )
			x = ipNuevo, mascaraNuevo, puertoNuevo #Se hace la tupla de key
			#self.lockTablaAlcanzabilidad.acquire()
			exite = self.tabla.get(x)
			if exite == None : #Si una entrada con ese Key NO existe, se crea
				#Se crea una nueva tupla
				self.tabla[x] = (distanciaNuevo + distanciaAtravezDe), atravezDe
			else:#Si existe una entrada con ese Key, se actualiza el valor de ser necesario
				#Se pregunta si el costo recibido es menor al que tenia, en caso de que si se atualiza
				if exite[0] > distanciaNuevo + distanciaAtravezDe:
					self.tabla[x] = (distanciaNuevo + distanciaAtravezDe), atravezDe
					self.bitacora.escribir("TablaAlcanzabilidad: " + "Se actualizo la distancia y el a traves de " + str(x) + " a distancia " + str(distanciaNuevo + distanciaAtravezDe) + " a traves " + str(atravezDe) )
			#self.lockTablaAlcanzabilidad.release()
			i = i + 1
		self.lockTablaAlcanzabilidad.release()#Se suelta el candado al final de la actualizacion

	#Metodo para agregar un alcanzable
	#alcanzable: no alcanzable, tupla (ip,mascara,puerto)
	#distanciaNuevo: costo entre alcanzable y atravezDe
	#atravezDe: tupla que es el intermediario entre el nodo y el destino, tupla (ip,mascara,puerto)
	def annadirAlcanzable(self, alcanzable, distanciaNuevo, atravezDe):
		self.lockTablaAlcanzabilidad.acquire()
		exite = self.tabla.get(alcanzable)
		if exite == None : #Si una entrada con ese Key NO existe, se crea
			#Se crea una nueva tupla
			self.tabla[alcanzable] = distanciaNuevo, atravezDe
			self.bitacora.escribir("TablaAlcanzabilidad: " + "Se annade el alcanzable " + str(alcanzable) + " a traves de " + str(atravezDe) + " con distancia " + str(distanciaNuevo))
		else:#Si existe una entrada con ese Key, se actualiza el valor de ser necesario
			print(str(alcanzable) + " este nodo no deberia existir en la tabla porque apenas esta llegando mensaje de aviso de que se desperto")
			self.bitacora.escribir("TablaAlcanzabilidad: " + str(alcanzable) + " este nodo no deberia existir en la tabla porque apenas esta llegando mensaje de aviso de que se desperto")
		self.lockTablaAlcanzabilidad.release()

	#Metodo para retornar lista de (ip, mascara, puerto, distancia) de los que conozco
	def obtenerTabla(self):
		self.lockTablaAlcanzabilidad.acquire()
		llaves = self.tabla.keys()
		tabla = list()
		for x in llaves:
			valor = self.tabla[x]
			tabla.append( (x[0],x[1],x[2],valor[0]) )
		self.lockTablaAlcanzabilidad.release()
		return tabla

	#Funcion encargada de retornar el nodo a traves por el cual se puede llegar al destino indicado
	#nodoDestino: nodo al que se quiere llegar, tupla (ip, mascara, puerto)
	def obtenerSiguienteNodo(self, nodoDestino):
		self.lockTablaAlcanzabilidad.acquire()
		sigNodo = self.tabla.get(nodoDestino)
		self.lockTablaAlcanzabilidad.release()
		return sigNodo[1]

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