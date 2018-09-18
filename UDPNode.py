#Modulo basico de todas las comunicaciones de networks en Python.
#Con ella podemos crear los sockets dentro de nuestro programa.
import socket
import subprocess
import threading
import multiprocessing

class Mensaje:
	def __init__(self,ip,puerto,mensaje):
		self.ip = ip
		self.puerto = puerto
		self.mensaje = mensaje

class UDPNode:
	mensajesRecibidos = list()
	def guardarMensaje(self,mensaje):
		self.mensajesRecibidos.append(mensaje)

	def recibeMensajes(self, serverSocket):
		while 1:
			message, clientAddress = serverSocket.recvfrom(2048)
			self.guardarMensaje(message)
			self.imprimirMensaje(message)

	def procRecibeMsg(self):
		print('UDP: Esta recibiendo mensajes en el fondo...\n')
		serverSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		serverSocket.bind(('25.8.90.106', 10001))
		thrdRecibeMensaje = threading.Thread(target = self.recibeMensajes, args=(serverSocket,))
		thrdRecibeMensaje.start()
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

	def imprimirMensaje(self, mensaje):
		ip = mensaje.ip
		puerto = mensaje.puerto
		bytesMensaje = mensaje.mensaje

		cantTuplas = int(codecs.encode(bytesMensaje[0:2], 'hex_codec'))
		i = 0
		print("IPf = " + str(ip) + " Puerto = " + str(puerto) + " dice : ")
		while i < cantTuplas:
			ipA = codecs.encode(bytesMensaje[(i*8)+2:(i*8)+3], 'hex_codec')
			ipB = codecs.encode(bytesMensaje[(i*8)+3:(i*8)+4], 'hex_codec')
			ipC = codecs.encode(bytesMensaje[(i*8)+4:(i*8)+5], 'hex_codec')
			ipD = codecs.encode(bytesMensaje[(i*8)+5:(i*8)+6], 'hex_codec')
			mascara = codecs.encode(bytesMensaje[(i*8)+6:(i*8)+7], 'hex_codec')
			costo = codecs.encode(bytesMensaje[(i*8)+7:(i*8)+10], 'hex_codec')
			print( str(ipA) + "." + str(ipB) + "." + str(ipC) + "." + str(ipD) + " " + str(mascara) + " " + str(costo) )
			i = i + 1

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
					'\t3. Cerrar servidor de mensajes.')
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
				bandera = False
				print('Se cerrara el menu.')
				clientSocket.close()
				thrdRecibeMensaje.terminate()
				thrdRecibeMensaje.join()
			else:
				print('Ingrese una opcion valida.')

if __name__ == '__main__':
	udp = UDPNode()
	udp.procRecibeMsg()
	udp.despligueMenuUDP()

#thrdRecibeMensaje.join()
#Tipo UDP y envio del Mensaje:
