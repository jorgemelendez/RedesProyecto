#Modulo basico de todas las comunicaciones de networks en Python.
#Con ella podemos crear los sockets dentro de nuestro programa.
import socket
import subprocess
import threading
import codecs
import multiprocessing
import sys
import os



class Mensaje:
	def __init__(self,ip,puerto,mensaje):
		self.ip = ip
		self.puerto = puerto
		self.mensaje = mensaje

class Red:
	def __init__(self,ipFuente,puertoFuente,ipRed, mascaraRed, costo):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente
		self.ipRed = ipRed
		self.mascaraRed = mascaraRed 
		self.costo = costo

	def soyEsaRed(self, ipRed, mascaraRed):
		if ipRed == self.ipRed and mascaraRed == self.mascaraRed:
			return True
		return False

	def soyEsaFuente(self, ipFuente, puertoFuente):
		if ipFuente == self.ipFuente and puertoFuente == self.puertoFuente:
			return True
		return False

	def costoMenor(self, costo):
		if costo < self.costo:
			return True
		return False

	def actualizarRed(self,ipFuente,puertoFuente,ipRed, mascaraRed, costo):
		self.ipFuente = ipFuente
		self.puertoFuente = puertoFuente
		self.ipRed = ipRed
		self.mascaraRed = mascaraRed 
		self.costo = costo

	def toString():
		ipFuente = self.ipFuente
		puertoFuente = self.puertoFuente
		ipRed = self.ipRed
		mascaraRed = self.mascaraRed 
		costo = self.costo


class TablaAlcanzabilidad:
	tabla = list()
	
	def __init__(self):
		self.tabla = list()

	def exiteRed(self, ipRed, mascaraRed):
		i = 0
		largo = len(self.tabla)
		while i < largo:
			if self.tabla[i].soyEsaRed(ipRed, mascaraRed) :
				return i
			i = i + 1
		return -1

	def imprimirTabla(self):
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

	def actualizarTabla(self, mensaje):
		ipFuenteNuevo = mensaje.ip
		puertoFuenteNuevo = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		while i < cantTuplas:
			ipRedNuevo = bytesMensaje[(i*8)+2:(i*8)+6]
			mascaraRedNuevo = bytesMensaje[(i*8)+6:(i*8)+7]
			costoNuevo = bytesMensaje[(i*8)+7:(i*8)+10]

			exite = self.exiteRed(ipRedNuevo, mascaraRedNuevo)
			if exite == -1 :
				#Se crea una nueva tupla
				self.tabla.append(Red(ipFuenteNuevo,puertoFuenteNuevo,ipRedNuevo, mascaraRedNuevo, costoNuevo))
			else:
				#se actualiza la tupla de ser necesario
				if self.tabla[i].costoMenor(costoNuevo) :
					self.tabla[i].actualizarRed(ipFuenteNuevo,puertoFuenteNuevo,ipRedNuevo, mascaraRedNuevo, costoNuevo);
				#Si el costo es mayor queda como antes
			i = i + 1

	def borrarFuente(self,ipFuente, puetoFuente):
		i = 0
		largo = len(self.tabla)
		while i < largo:
			if self.tabla[i].soyEsaFuente(ipFuente, puetoFuente) :
				self.tabla.pop(i)
			i = i + 1

class UDPNode:
	
	mensajesRecibidos = list()
	tablaAlcanzabilidad = TablaAlcanzabilidad()

	def guardarMensaje(self,mensaje):
		self.mensajesRecibidos.append(mensaje)




	def recibeMensajes(self, serverSocket):
		while 1:
			message, clientAddress = serverSocket.recvfrom(2048)
			mensaje = Mensaje(clientAddress[0],clientAddress[1], message)
			#flag = self.revisaMensaje(message)
			self.guardarMensaje(mensaje)
			self.imprimirMensaje(mensaje)
			self.tablaAlcanzabilidad.actualizarTabla(mensaje)


	def procRecibeMsg(self, ip, puerto):
		print('UDP: Esta recibiendo mensajes en el fondo...\n')
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		serverSocket.bind((ip, puerto))
		self.recibeMensajes(serverSocket)

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

	def imprimirMensajes(self):
		i = 0
		largo = len(self.mensajesRecibidos)
		while i < largo:
			self.imprimirMensaje( self.mensajesRecibidos[i] )
			i = i + 1

	#Metodo que envia un mensaje mediante UDP al IP + socket que esocgio al inicio.
	def envioMensajeUDP(self, mensaje):
			message = mensaje
			print(message)
			serverNameS = input('Ingrese el IP del servidor al que quiere enviar el mensaje: ')
			serverPortS = input('Ingrese el puerto al que desea enviar: ')
			clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
			clientSocket.sendto(message, (serverNameS, int(serverPortS)))
			clientSocket.close()
			print('El mensaje fue enviado.\n')

	def tuplaToBytes(self, tupla):
	    tupladiv = tupla.split(' ')
	    numeroip = tupladiv[0]
	    myip = numeroip.split('.')
	    bytesmios = bytearray()
	    for x in range(0, 4):
	        ipnum = int(myip[x])
	        bytesmios += (ipnum).to_bytes(1, byteorder='big')
	    masc = int(tupladiv[1])
	    bytesmios += (masc).to_bytes(1, byteorder='big')
	    costo = int(tupladiv[2])
	    bytesmios += (costo).to_bytes(3, byteorder='big')
	    #print(bytesmios)
	    return bytesmios

	def leerMensaje(self):
		print('Ingrese la cantidad de tuplas que quiere enviar:')
		entradas = input()
		vectorBytes = bytearray((int(entradas)).to_bytes(2, byteorder='big'))
		i = 0
		
		while i < int(entradas):
			print('Ingrese la tupla:')
			tupla = input()
			vectorBytes += self.tuplaToBytes(tupla)
			i = i + 1
			print('\n')
		return vectorBytes

	#Metodo que despliega Menu principal de UDP
	def despligueMenuUDP(self):
		print('Menu principal del modulo de Red UDP: \n'
					'\t1. Enviar un mensaje. \n'
					'\t2. Ver mensajes recibidos. \n'
					'\t3. Imprimir tabla de alcanzabilidad.\n'
					'\t4. Cerrar servidor de mensajes.')
		bandera = True
		while bandera == True:
			taskUsuario = input('Que desea hacer:')
			if taskUsuario == '1':
				mensajebytes = self.leerMensaje()
				self.envioMensajeUDP(mensajebytes)
			elif taskUsuario == '2':
				print('Estos son sus mensajes:')
				self.imprimirMensajes()
			elif taskUsuario == '3':
				print("\n\n")
				print('Tabla de alcanzabilidad:')
				self.tablaAlcanzabilidad.imprimirTabla()
				print("\n\n")
			elif taskUsuario == '4':
				bandera = False
				os._exit(1)
				print('Se cerrara el menu.')

			else:
				print('Ingrse opcion valida.')

if __name__ == '__main__':
	udp = UDPNode()
	ip = input('Ip;')
	puerto = input('Puerto:')
	thrdRecibeMensaje = threading.Thread(target = udp.procRecibeMsg, args = (ip, int(puerto),))
	thrdRecibeMensaje.start()
	udp.despligueMenuUDP()

