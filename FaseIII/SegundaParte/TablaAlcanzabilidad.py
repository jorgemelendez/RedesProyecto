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
	def __init__(self, bitacora, lockAbortarActualizaciones, abortarActualizaciones):
		self.bitacora = bitacora
		self.parser = dict()
		self.lockParser = threading.Lock()
		self.tabla = dict() #El formato va a ser:  key=(ip,mascara,puerto) valor=(costo,(ip,mascara,puerto))
		self.lockTablaAlcanzabilidad = threading.Lock()
		self.lockAbortarActualizaciones = lockAbortarActualizaciones
		self.abortarActualizaciones = abortarActualizaciones

	def modificarCosto(self, key, costoNuevo):
		self.lockTablaAlcanzabilidad.acquire()
		self.tabla[key] = costoNuevo, self.tabla[key][1]
		self.lockTablaAlcanzabilidad.release()

	#Metodo para borrar la tabla de alcanzabilidad
	#vecinosActivos: tuplas de la forma (ip, mascara, puerto, distancia)
	def limpiarPonerVecinosActivos(self, vecinosActivos):
		self.lockTablaAlcanzabilidad.acquire()
		self.lockParser.acquire()
		self.tabla.clear()
		self.parser.clear()
		for x in vecinosActivos:
			vecino = (x[0],x[1],x[2])
			self.tabla[vecino] = x[3], vecino
			self.parser[(vecino[0],vecino[2])] = vecino
		self.lockParser.release()
		self.lockTablaAlcanzabilidad.release()
		self.bitacora.escribir("Se borra la tabla de alcanzabilidad y se ponen solo los vecinos activos")

	#Metodo que imprime la tabla de alcanzabilidad del nodo
	def imprimirTabla(self):
		self.lockTablaAlcanzabilidad.acquire()
		llaves = self.tabla.keys()
		i = 0
		for x in llaves:
			valor = self.tabla[x]
			print( str(i) + ": " + str(x) + " " + str(valor[0]) + " " + str(valor[1]) )
			i = i + 1
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
		self.lockParser.acquire()
		del self.tabla[(ip, mascara, puerto)]
		del self.tabla[(ip, puerto)]
		self.lockParser.release()
		self.lockTablaAlcanzabilidad.release()
		self.bitacora.escribir("TablaAlcanzabilidad: " + "Se borra el alcanzable " + str((ip,mascara,puerto)))

	#Metodo para borrar un alcanzable de la tabla
	# borra las tuplas que su a traves ser (ip,mascara,puerto)
	#ip: ip del alcanzable que se quiere borrar
	#mascara: mascara del alcanzable que se quiere borrar
	#puerto: puerto del alcanzable que se quiere borrar
	def borrarAtravez(self,ip, mascara, puerto):
		self.lockTablaAlcanzabilidad.acquire()
		self.lockParser.acquire()
		listaEliminar = list()
		llaves = self.tabla.keys()
		for x in llaves:
			valor = self.tabla[x]
			if valor[1] == (ip,mascara,puerto):
				listaEliminar.append(x)
		for x in listaEliminar:
			del self.tabla[x]
			del self.tabla[(x[0],x[2])]
		self.lockParser.release()
		self.lockTablaAlcanzabilidad.release()
		self.bitacora.escribir("TablaAlcanzabilidad: " + "Se borra todos los alcanzables que se llegaba a traves de" + str((ip,mascara,puerto)))

	#Metodo para actualizar la tabla cuando llega un mensaje de actializacio de tabla
	#mensaje: actualizacion recibido (2bytes de cantidad de tuplas, 
	#      tuplas (ip,mascara,puerto,distancia))
	#atravezDe: tupla que es el intermediario entre el nodo y el destino, tupla (ip,mascara,puerto)
	#distanciaAtravezDe: distancia del vecino para tomarla en cuenta en la actualizacion
	def actualizarTabla(self, mensaje, atravezDe, distanciaAtravezDe):
		self.lockTablaAlcanzabilidad.acquire()#Se agarra el candadi aqui para que la actualizacion se de completa
		self.lockAbortarActualizaciones.acquire()
		abortar = self.abortarActualizaciones
		self.lockAbortarActualizaciones.release()
		if abortar == False:
			self.lockParser.acquire()
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
					self.parser[(x[0],x[2])] = x
				else:#Si existe una entrada con ese Key, se actualiza el valor de ser necesario
					#Se pregunta si el costo recibido es menor al que tenia, en caso de que si se atualiza
					if exite[0] > distanciaNuevo + distanciaAtravezDe:
						self.tabla[x] = (distanciaNuevo + distanciaAtravezDe), atravezDe
						self.bitacora.escribir("TablaAlcanzabilidad: " + "Se actualizo la distancia y el a traves de " + str(x) + " a distancia " + str(distanciaNuevo + distanciaAtravezDe) + " a traves " + str(atravezDe) )
				#self.lockTablaAlcanzabilidad.release()
				i = i + 1
			self.lockParser.release()
		else:
			self.bitacora.escribir("ABORTE ACTUALIZACION")
		self.lockTablaAlcanzabilidad.release()#Se suelta el candado al final de la actualizacion

	#Metodo para agregar un alcanzable
	#alcanzable: no alcanzable, tupla (ip,mascara,puerto)
	#distanciaNuevo: costo entre alcanzable y atravezDe
	#atravezDe: tupla que es el intermediario entre el nodo y el destino, tupla (ip,mascara,puerto)
	def annadirAlcanzable(self, alcanzable, distanciaNuevo, atravezDe):
		self.lockTablaAlcanzabilidad.acquire()
		self.lockParser.acquire()
		exite = self.tabla.get(alcanzable)
		if exite == None : #Si una entrada con ese Key NO existe, se crea
			#Se crea una nueva tupla
			self.tabla[alcanzable] = distanciaNuevo, atravezDe
			self.parser[(alcanzable[0],alcanzable[2])] = alcanzable
			self.bitacora.escribir("TablaAlcanzabilidad: " + "Se annade el alcanzable " + str(alcanzable) + " a traves de " + str(atravezDe) + " con distancia " + str(distanciaNuevo))
		else:
			#print(str(alcanzable) + " este nodo no deberia existir en la tabla porque apenas esta llegando mensaje de aviso de que se desperto")
			self.bitacora.escribir("TablaAlcanzabilidad: " + str(alcanzable) + " este nodo no deberia existir en la tabla porque apenas esta llegando mensaje de aviso de que se desperto")
		self.lockParser.release()
		self.lockTablaAlcanzabilidad.release()

	#Metodo para retornar lista de (ip, mascara, puerto, distancia) de los que conozco
	def obtenerTabla(self):
		self.lockTablaAlcanzabilidad.acquire()
		llaves = self.tabla.keys()
		tabla = list()
		for x in llaves:
			valor = self.tabla[x]
			tabla.append( (x[0],x[1],x[2],valor[1][0],valor[1][1],valor[1][2],valor[0]) )
		self.lockTablaAlcanzabilidad.release()
		return tabla

	#Funcion encargada de retornar el nodo a traves por el cual se puede llegar al destino indicado
	#nodoDestino: nodo al que se quiere llegar, tupla (ip, mascara, puerto)
	def obtenerSiguienteNodo(self, nodoDestino):
		self.lockTablaAlcanzabilidad.acquire()
		sigNodo = self.tabla.get(nodoDestino)
		self.lockTablaAlcanzabilidad.release()
		return sigNodo[1]

	#Funcion encargada de retornar (ip,mascara,puerto) dado (ip,puerto)
	#nodo: tupla (ip, puerto)
	def obtenerKey(self, nodo):
		self.lockParser.acquire()
		key = self.parser.get(nodo)
		self.lockParser.release()
		return key